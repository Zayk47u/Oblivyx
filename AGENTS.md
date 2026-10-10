# Oblivyx app distribution

The owner requested that all new apps we make be added to `Zayk47u/Oblivyx` so they can access them from one Feather source:

`https://raw.githubusercontent.com/Zayk47u/Oblivyx/main/app-repo.json`

For new iOS apps and updates, publish the approved physical-device IPA here and retain existing apps and versions. Use `apps/<slug>.json`, an app icon under `assets/icons/`, and the publishing workflow. Record exact bundle ID, version/build, minimum iOS, size, and SHA-256. Verify the workflow, anonymous source retrieval, and release download before reporting success.

The owner uses Feather to sign the IPA. Publish unsigned builds unless the owner changes that preference. Never commit signing credentials, personal context, private app source, or secret-bearing artifact URLs. This repository is public and is the app distribution catalog; app development can stay in its own repository.

Preserve the original README title/tagline and all existing catalog entries. Do not advertise an app until its durable GitHub release asset is verified. The publisher generates `app-repo.json`; do not replace it with a temporary Expo artifact URL.

Run `python3 -m unittest discover -s tests -v` and `python3 scripts/publish_catalog.py --validate-only` when changing the publisher or descriptors. New app publication is performed when a build is ready; this catalog does not autonomously build unfinished apps.
