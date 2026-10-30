# Oblivyx
Experimental applications for experimental people

## What this repository contains

Oblivyx is an iOS app distribution catalog with repository-specific Python maintenance tools. It is **not the source repository for the distributed apps**, an app builder, or a general-purpose package.

- **Catalog publisher:** validates app descriptors and IPA size, SHA-256, archive integrity, bundle identifier, version/build, minimum iOS, and device platform; publishes versioned GitHub release assets; generates a Feather source while retaining earlier versions.
- **Public product discoveries:** transforms public store catalogs into clothing discovery feeds. Individual store failures retain cached products; an all-store failure leaves that feed unchanged.
- **Tests:** Python unittest coverage for catalog/version preservation, release retry behavior, checksum conflicts, descriptor/archive validation, product transformation, and cached-feed behavior.

The scripts are currently tied to this repository's catalog, paths, and configured stores. Public visibility does not itself grant an open-source license. No project-wide source-code license is currently declared; third-party font notices apply only to the identified fonts. App binaries, branding, images, and store data are separate materials—not automatically licensed with the Python tooling.

## Check the tooling locally

Use Python 3.11 or newer; the publisher uses `hashlib.file_digest`. From a local checkout:

```sh
git clone https://github.com/Zayk47u/Oblivyx.git
cd Oblivyx
python3 -m unittest discover -s tests -v
python3 scripts/publish_catalog.py --validate-only
```

These commands run local tests and descriptor validation, not release publication. Tests use mocks, synthetic IPA archives, and temporary files. They do not prove that an app runs on a physical iPhone. No third-party Python package installation is required by these scripts.

**Do not omit `--validate-only` for a local check.** The publishing path uses authenticated `gh`, `curl`, and GitHub Actions environment variables to create/upload/publish releases. `--verify-ipa /path/to/app.ipa` additionally checks an archive, but currently requires a catalog containing exactly one app; the live catalog contains more than one.

Running `scripts/refresh_discoveries.py` directly contacts configured stores and writes local feed files. The local unit tests are the appropriate first check instead. The scheduled workflow also commits refreshed feed data.

See [CONTRIBUTING.md](CONTRIBUTING.md) for change boundaries and review guidance. Never submit credentials, signing certificates, private app source, personal records, or unapproved artifacts.

## App catalog

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
| CONTINUUM | 0.1.0, build 1 | 16.4 | Local Calibrate drafts and Spark brainstorming; unsigned |
| Sample Size | 0.7.0, build 7 | 16.4 | Shared app/site workspace, Grailed/Depop discovery and polished review UI; unsigned |

[Sample Size v0.7.0](https://github.com/Zayk47u/Oblivyx/releases/tag/sample-size-v0.7.0-b7) connects saved inspiration and the working library to the existing private Brand Review site. Saved/pass/later decisions, exact notes and tags, collections, image notes, discussions, reference/casting files and revisions, casting selections, sources, preferences, drafts and inbox state share one workspace. Existing design ratings, feedback, decisions and weighted criteria retain exact-version sync.

Update over the existing app with the same Feather signing identity, then keep Sample Size open until its connection strip reports **Workspace synced**. Saved brand inspiration appears in **Work → References** and the site's **References** section. The full site workspace is available at **App workspace**. Conflicting field edits require a choice; original attachments upload before records are marked synced.

Grailed and Depop searches and photo galleries remain available through the private site connection. Followed searches refresh every six hours while active or on return; cached results survive provider failures. No closed-app background refresh, personal marketplace-account connection or visual AI training is claimed. Website editing coverage varies by data type.

The UI now uses quieter dark/sage colors, compact Saved actions, tucked-away filters and nonshrinking Work tabs. 48 app tests, 15 site tests, 9 distribution tests, typecheck/lint, authenticated local file/record roundtrips, conflict/isolation checks and browser flows passed. The unsigned arm64 IPA, 142 bundled images/fonts, public release checksum and catalog were verified. Physical iPhone runtime and the live-account roundtrip remain unverified; the desktop sign-in session expired.

The public clothing feed is generated by `scripts/refresh_discoveries.py` and `.github/workflows/refresh-discoveries.yml`. A failed store retains its last good products; all-store failure keeps the prior published feed. Only public product catalog data is used; no shopping account, Pinterest login or user reference library is included in the public feed.

[CONTINUUM v0.1.0](https://github.com/Zayk47u/Oblivyx/releases/tag/continuum-v0.1.0-b1) provides native Home, Work, Life, Chaos, and Control screens, adaptive Quick Calibrate with review/edit/skip, and persistent local drafts and Spark history/favorites. No personal records or live Continuity/AI provider are connected. Local storage is unencrypted. Native tests and two iOS simulator flows passed; physical iPhone signing/runtime remains untested. Its public release download and SHA-256 were verified.

## Publish another app or update

1. Build an iPhone `.ipa` and verify its bundle identifier, version/build, minimum iOS, byte size, and SHA-256.
2. Add an icon under `assets/icons/` and a descriptor under `apps/<slug>.json`. Use `apps/sample-size.json` as the example. For updates, append a version to the existing app descriptor; retain the older versions.
3. Set `sourceURL` to the approved build artifact's public HTTPS download URL. Never put access tokens, signing credentials, or private source code in this repository.
4. Validate locally: `python3 scripts/publish_catalog.py --validate-only`. For the first single-app catalog, add `--verify-ipa /path/to/app.ipa` to check the actual archive too.
5. Commit to `main`. The **Publish Feather catalog** action verifies the IPA checksum and embedded metadata, uploads it to a GitHub Release, and updates `app-repo.json` after the download is available.

The same source URL lists every published app. Catalog releases use immutable app/version/build tags. An existing asset with a different checksum is rejected instead of overwritten. Already published assets do not depend on the original build service URL remaining active.

The workflow can also be rerun manually from the repository's Actions tab. Publishing failures leave the existing catalog intact. Do not edit `app-repo.json` directly; it is generated from the descriptors after release verification.

This is a public repository: release IPAs, icons, and app descriptions are publicly downloadable.

Sample Size uses Unifraktur Cook and Barlow Condensed under the SIL Open Font License. [Font licenses](assets/licenses/sample-size-fonts.txt).

