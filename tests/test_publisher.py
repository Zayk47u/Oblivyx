import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import plistlib
import tempfile
import unittest
from unittest.mock import patch
import zipfile

spec = importlib.util.spec_from_file_location("publisher", Path(__file__).parents[1] / "scripts/publish_catalog.py")
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


class PublisherTests(unittest.TestCase):
    def setUp(self):
        self.app = p.load_apps(p.ROOT / "apps")[0]
        self.version = self.app["versions"][0]

    def test_catalog_preserves_apps_and_prior_versions(self):
        apps = copy.deepcopy([self.app, self.app])
        apps[1]["slug"] = "another-app"
        apps[1]["bundleIdentifier"] = "com.zay.another"
        old = copy.deepcopy(apps[0]["versions"][0])
        old["version"] = "0.0.9"
        apps[0]["versions"].append(old)
        catalog = p.make_catalog(apps)
        self.assertEqual(len(catalog["apps"]), 2)
        self.assertEqual(len(catalog["apps"][0]["versions"]), 2)
        self.assertEqual(catalog["apps"][0]["downloadURL"], catalog["apps"][0]["versions"][0]["downloadURL"])
        self.assertIn("/releases/download/", catalog["apps"][0]["downloadURL"])
        self.assertNotIn("sourceURL", json.dumps(catalog))

    def test_published_asset_skips_expired_build_url(self):
        asset = {"name": self.version["fileName"], "state": "uploaded", "size": self.version["size"], "digest": "sha256:" + self.version["sha256"]}
        with patch.object(p, "release_for", return_value={"draft": False, "assets": [asset]}), patch.object(p, "run") as run:
            p.publish_version(self.app, self.version, Path("unused"))
            run.assert_not_called()

    def test_checksum_conflict_refuses_existing_asset(self):
        asset = {"state": "uploaded", "size": self.version["size"], "digest": "sha256:" + "0" * 64}
        with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
            p.check_asset(asset, self.version)

    def test_wrong_app_rejected_even_with_valid_archive_checksum(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "wrong.ipa"
            info = {"CFBundleIdentifier": "com.someone.else", "CFBundleShortVersionString": self.version["version"], "CFBundleVersion": self.version["buildVersion"], "MinimumOSVersion": self.version["minOSVersion"], "CFBundleSupportedPlatforms": ["iPhoneOS"]}
            with zipfile.ZipFile(path, "w") as z:
                z.writestr("Payload/Wrong.app/Info.plist", plistlib.dumps(info))
            version = dict(self.version, size=path.stat().st_size, sha256=hashlib.sha256(path.read_bytes()).hexdigest())
            with self.assertRaisesRegex(ValueError, "CFBundleIdentifier mismatch"):
                p.verify_ipa(path, self.app, version)

    def test_duplicate_app_and_bad_descriptor_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sample-size.json").write_text(json.dumps(self.app))
            another = copy.deepcopy(self.app)
            another["slug"] = "another-app"
            (root / "another-app.json").write_text(json.dumps(another))
            with self.assertRaisesRegex(ValueError, "Duplicate bundle identifier"):
                p.load_apps(root)
            (root / "another-app.json").unlink()
            self.app["versions"][0]["fileName"] = "../../unsafe.ipa"
            (root / "sample-size.json").write_text(json.dumps(self.app))
            with self.assertRaisesRegex(ValueError, "Invalid IPA file name"):
                p.load_apps(root)


if __name__ == "__main__":
    unittest.main()
