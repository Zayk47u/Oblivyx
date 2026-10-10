# Oblivyx
Experimental applications for experimental people

Zay's shared app catalog. This is the default distribution home for the iOS apps we make.

## Add to Feather

[Open in Feather](feather://source/https://raw.githubusercontent.com/Zayk47u/Oblivyx/main/app-repo.json)

If your browser does not open Feather, copy this URL into **Feather → Sources → + → Source URL → Save**:

```text
https://raw.githubusercontent.com/Zayk47u/Oblivyx/main/app-repo.json
```

Add the source once. Refresh Sources for new apps and releases. Feather signs the unsigned IPA using the certificate configured on your device.

## Apps

| App | Current preview | Minimum iOS | Status |
| --- | --- | --- | --- |
| Sample Size | 0.1.0, build 1 | 16.4 | Offline clothing taste, collections, design review, and export; unsigned |

Sample Size includes 113 bundled references and design images. Live shopping feeds and automatic website sync are still in development. Installation and runtime on an iPhone have not yet been verified.

## Publish another app or update

1. Build an iPhone `.ipa` and verify its bundle identifier, version/build, minimum iOS, byte size, and SHA-256.
2. Add an icon under `assets/icons/` and a descriptor under `apps/<slug>.json`. Use `apps/sample-size.json` as the example. For updates, append a version to the existing app descriptor; retain the older versions.
3. Set `sourceURL` to the approved build artifact's public HTTPS download URL. Never put access tokens, signing credentials, or private source code in this repository.
4. Validate locally: `python3 scripts/publish_catalog.py --validate-only`. For the first single-app catalog, add `--verify-ipa /path/to/app.ipa` to check the actual archive too.
5. Commit to `main`. The **Publish Feather catalog** action verifies the IPA checksum and embedded metadata, uploads it to a GitHub Release, and updates `app-repo.json` after the download is available.

The same source URL lists every published app. Catalog releases use immutable app/version/build tags. An existing asset with a different checksum is rejected instead of overwritten. Already published assets do not depend on the original build service URL remaining active.

The workflow can also be rerun manually from the repository's Actions tab. Publishing failures leave the existing catalog intact. Do not edit `app-repo.json` directly; it is generated from the descriptors after release verification.

This is a public repository: release IPAs, icons, and app descriptions are publicly downloadable.
