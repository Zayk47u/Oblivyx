# Contributing to Oblivyx

Oblivyx is a repository-specific iOS distribution catalog with Python publisher and product-discovery tools. App development and private app source belong elsewhere. Read [AGENTS.md](AGENTS.md) before proposing a change.

## Before contributing

No project-wide source-code license is currently declared. Ask the maintainer to clarify licensing before reuse or submitting a substantial code contribution. Font notices do not license the scripts, app binaries, or other assets. Do not assume rights to redistribute third-party content.

Use a focused branch and propose a pull request for maintainer review; do not push directly to `main`. Explain the problem, the files changed, the checks actually run, and any remaining limitations. Never fabricate successful checks. Publishing an app or adding public assets requires explicit owner approval, not merely a documentation or code review.

## Local checks

Use Python 3.11 or newer. From the repository root:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/publish_catalog.py --validate-only
```

The scripts use Python's standard library. The tests use mocked release operations, synthetic archive data, and temporary directories; they do not need a signing certificate or an actual iPhone. Run both checks when changing the publisher or descriptors. Add a focused regression test for a behavior change.

- `tests/test_publisher.py`: catalog history, existing assets, checksum conflicts, draft-release retries, archive metadata, and invalid descriptors.
- `tests/test_discoveries.py`: product transformation, unavailable products, cached store fallback, and all-store failure.

These are commands to run—not a claim that checks passed for a proposed change. Report their actual results in your pull request.

## Keep validation separate from publication

- Keep `--validate-only` on the publisher command during local descriptor checks. Without it, the script enters the release-publishing path.
- Real publishing requires `gh`, `curl`, authentication, and the expected GitHub Actions environment. Do not trigger or rerun publishing workflows merely to test documentation.
- The publishing workflow runs on qualifying `main` pushes or manual dispatch. It runs unit tests, verifies/publishes releases, and commits the generated catalog.
- The discovery workflow contacts stores and can commit refreshed feeds. Running its Python script locally also writes feed files; use unit tests first.
- `--verify-ipa` currently requires exactly one app descriptor. Do not remove live catalog entries to satisfy that restriction.

## Preserve existing releases and private information

Retain the README title/tagline, apps, older versions, and release history. Update app descriptors rather than editing generated `app-repo.json`. Do not replace durable release URLs with temporary build links or overwrite assets with different checksums.

Never include tokens, signing material, private source, personal records, or secret-bearing URLs in commits, issue reports, screenshots, or logs. Use synthetic fixtures. Keep proposed tooling changes separate from app binaries, branding, third-party images, and store content.
