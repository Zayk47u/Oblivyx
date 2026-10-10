#!/usr/bin/env python3
"""Verify approved IPAs, publish immutable releases, then build the Feather source."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import subprocess
import tempfile
from datetime import datetime
from urllib.parse import urlparse
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "Zayk47u/Oblivyx"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def https_url(value):
    u = urlparse(value)
    require(u.scheme == "https" and u.hostname and not u.username and not u.password,
            "URLs must be public HTTPS URLs without embedded credentials")


def load_apps(directory):
    apps = []
    ids = set()
    slugs = set()
    for path in sorted(directory.glob("*.json")):
        app = json.loads(path.read_text())
        slug = app["slug"]
        require(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug), "Invalid app slug")
        require(path.stem == slug and slug not in slugs, "Duplicate or mismatched slug")
        require(re.fullmatch(r"[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+", app["bundleIdentifier"]), "Invalid bundle identifier")
        require(app["bundleIdentifier"] not in ids, "Duplicate bundle identifier")
        ids.add(app["bundleIdentifier"])
        slugs.add(slug)
        for field in ("name", "developerName", "subtitle", "localizedDescription"):
            require(isinstance(app[field], str) and app[field], f"Missing {field}")
        icon = app["iconPath"]
        require(icon.startswith("assets/") and ".." not in Path(icon).parts and (ROOT / icon).is_file(), "Missing local icon")
        require(re.fullmatch(r"[0-9A-Fa-f]{6}", app["tintColor"]), "Invalid tint color")
        require(app["versions"], "App must have a version")
        seen = set()
        for v in app["versions"]:
            for key in ("version", "buildVersion"):
                require(isinstance(v[key], str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.+-]*", v[key]), f"Invalid {key}")
            key = (v["version"], v["buildVersion"])
            require(key not in seen, "Duplicate version/build")
            seen.add(key)
            datetime.fromisoformat(v["date"].replace("Z", "+00:00"))
            require(re.fullmatch(r"\d+\.\d+(?:\.\d+)?", v["minOSVersion"]), "Invalid minimum iOS")
            require(type(v["size"]) is int and v["size"] > 0, "Invalid IPA size")
            require(re.fullmatch(r"[0-9a-f]{64}", v["sha256"]), "Invalid SHA-256")
            require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*\.ipa", v["fileName"]), "Invalid IPA file name")
            https_url(v["sourceURL"])
        app["versions"].sort(key=lambda v: (datetime.fromisoformat(v["date"].replace("Z", "+00:00")), v["buildVersion"]), reverse=True)
        apps.append(app)
    require(apps, "Catalog cannot be empty")
    return apps


def tag_for(app, version):
    return f"{app['slug']}-v{version['version']}-b{version['buildVersion']}"


def verify_ipa(path, app, version):
    require(path.stat().st_size == version["size"], "IPA size mismatch")
    with path.open("rb") as f:
        digest = hashlib.file_digest(f, "sha256").hexdigest()
    require(digest == version["sha256"], "IPA SHA-256 mismatch")
    with zipfile.ZipFile(path) as z:
        require(z.testzip() is None, "Corrupt IPA archive")
        infos = [n for n in z.namelist() if n.startswith("Payload/") and n.count("/") == 2 and n.endswith(".app/Info.plist")]
        require(len(infos) == 1, "IPA must contain one main app")
        info = plistlib.loads(z.read(infos[0]))
        for field, expected in (("CFBundleIdentifier", app["bundleIdentifier"]),
                                ("CFBundleShortVersionString", version["version"]),
                                ("CFBundleVersion", version["buildVersion"]),
                                ("MinimumOSVersion", version["minOSVersion"])):
            require(info.get(field) == expected, f"IPA {field} mismatch")
        require(info.get("CFBundleSupportedPlatforms") == ["iPhoneOS"], "IPA must target physical iOS devices")
    return digest


def run(*args):
    return subprocess.run(args, check=True, text=True, capture_output=True).stdout


def release_for(tag):
    p = subprocess.run(["gh", "api", f"repos/{REPOSITORY}/releases/tags/{tag}"], text=True, capture_output=True)
    if p.returncode:
        if "HTTP 404" in p.stderr:
            return None
        raise RuntimeError(p.stderr)
    return json.loads(p.stdout)


def check_asset(asset, version):
    require(asset["state"] == "uploaded" and asset["size"] == version["size"], "Release asset incomplete or wrong size")
    digest = asset.get("digest")
    require(not digest or digest == "sha256:" + version["sha256"], "Release asset digest differs; refusing to overwrite")


def publish_version(app, version, work):
    tag = tag_for(app, version)
    release = release_for(tag)
    asset = next((a for a in release["assets"] if a["name"] == version["fileName"]), None) if release else None
    if asset:
        check_asset(asset, version)
        # Old releases remain usable after the original build service URL expires.
        if not asset.get("digest"):
            download = work / version["fileName"]
            run("gh", "release", "download", tag, "--repo", REPOSITORY, "--pattern", version["fileName"], "--dir", str(work))
            verify_ipa(download, app, version)
    else:
        download = work / version["fileName"]
        run("curl", "--fail", "--location", "--silent", "--show-error", "--retry", "3", "--connect-timeout", "30", "--max-time", "600", "--output", str(download), version["sourceURL"])
        verify_ipa(download, app, version)
        if release is None:
            notes = work / "release-notes.md"
            notes.write_text(f"{app['localizedDescription']}\n\n{version.get('localizedDescription', '')}\n\n"
                             f"Bundle: `{app['bundleIdentifier']}`\n\nSHA-256: `{version['sha256']}`\n")
            run("gh", "release", "create", tag, "--repo", REPOSITORY, "--target", os.environ["GITHUB_SHA"],
                "--title", f"{app['name']} {version['version']} (build {version['buildVersion']})", "--notes-file", str(notes), "--draft")
        run("gh", "release", "upload", tag, str(download), "--repo", REPOSITORY)
        release = release_for(tag)
        asset = next(a for a in release["assets"] if a["name"] == version["fileName"])
        check_asset(asset, version)
    if release["draft"]:
        run("gh", "release", "edit", tag, "--repo", REPOSITORY, "--draft=false", "--latest=false")
    print(f"Verified {tag}: {asset['size']} bytes")


def make_catalog(apps):
    raw = f"https://raw.githubusercontent.com/{REPOSITORY}/main/"
    catalog = {"name": "Oblivyx", "identifier": "com.zay.oblivyx.catalog",
               "subtitle": "Experimental applications for experimental people",
               "description": "Zay's app collection. Add this source once in Feather, then refresh it for new apps and versions.",
               "website": f"https://github.com/{REPOSITORY}",
               "iconURL": "https://avatars.githubusercontent.com/u/164645480?v=4",
               "apps": [], "news": []}
    for app in apps:
        item = {k: app[k] for k in ("name", "bundleIdentifier", "developerName", "subtitle", "localizedDescription", "tintColor")}
        item.update(iconURL=raw + app["iconPath"], beta=app.get("beta", False), appPermissions=app.get("appPermissions", {}), versions=[])
        for v in app["versions"]:
            version = {k: v[k] for k in ("version", "buildVersion", "date", "size", "minOSVersion")}
            version["localizedDescription"] = v.get("localizedDescription", "")
            version["downloadURL"] = f"https://github.com/{REPOSITORY}/releases/download/{tag_for(app, v)}/{v['fileName']}"
            item["versions"].append(version)
        latest = item["versions"][0]
        item.update(version=latest["version"], versionDate=latest["date"], size=latest["size"], downloadURL=latest["downloadURL"])
        catalog["apps"].append(item)
    return catalog


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--verify-ipa", type=Path)
    args = parser.parse_args()
    apps = load_apps(ROOT / "apps")
    if args.verify_ipa:
        require(len(apps) == 1, "Local IPA check requires one app")
        verify_ipa(args.verify_ipa, apps[0], apps[0]["versions"][0])
    if args.validate_only:
        print(f"Validated {len(apps)} app descriptor(s)")
        return
    require(os.environ.get("GITHUB_REPOSITORY") == REPOSITORY, "Run publishing in the authorized distribution repository")
    for app in apps:
        for version in app["versions"]:
            with tempfile.TemporaryDirectory() as directory:
                publish_version(app, version, Path(directory))
    (ROOT / "app-repo.json").write_text(json.dumps(make_catalog(apps), indent=2) + "\n")


if __name__ == "__main__":
    main()
