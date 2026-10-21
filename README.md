# Zshbin

[![CI](https://github.com/cheeseonamonkey/Zshbin/actions/workflows/ci.yml/badge.svg)](https://github.com/cheeseonamonkey/Zshbin/actions/workflows/ci.yml)

A standalone, GitHub-backed pastebin. Migrated from [ShipHero/shbin](https://github.com/Shiphero/shbin) (MIT license); see [LICENSE](LICENSE).

> **Security status:** Bootstrap only. Encryption, expiration, private sharing, MCP, and history compaction are **not implemented**. The migrated CLI can upload **public plaintext only**, and requires an explicit `--public` flag. Do not upload secrets.

## Install (development)

Requires Python 3.10+ and [uv](https://docs.astral.sh/uv/).

```sh
uv tool install 'git+https://github.com/cheeseonamonkey/Zshbin.git'
```

## Authenticate

Use the GitHub CLI instead of inheriting the upstream OAuth application's credentials:

```sh
gh auth login
zshbin auth             # save the target repository (no access token stored)
```

Alternatively, set `ZSHBIN_GITHUB_TOKEN` and `ZSHBIN_REPO`. Use a fine-grained token restricted to the intended repository. The GitHub API writer currently uses repository Contents permissions, which GitHub does **not** restrict by file path.

## Legacy CLI (public uploads only)

```sh
zshbin --help
zshbin file.txt --public
zshbin dl path/in/repo/file.txt
```

The baseline uploader writes to its configured repository's **default branch**. Do not configure your source-code repository as an upload target; use a **separate data repository** until the isolated data-branch backend is implemented.

## Website

The static landing page lives in [site/](site/). [Pages deployment workflow](.github/workflows/pages.yml) is included, but deployment requires selecting **GitHub Actions** in **Settings → Pages**.

After enabling, the expected URL is https://cheeseonamonkey.github.io/Zshbin/ (not verified live yet).

## Design

See [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) for the hardened design, security boundaries, and phased implementation roadmap.

## Local checks

```sh
uv sync --group dev
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
```

## Status

- [x] Standalone public repository with new history
- [x] Baseline CLI migration, independently named package, CI, Pages scaffold
- [x] Stop using upstream OAuth client ID; explicit opt-in for plaintext uploads
- [ ] Isolated storage branch/repository and atomic manifest
- [ ] Encrypted-by-default uploads and client-side decryption
- [ ] OAuth/allowlisted browser uploads, optional restricted key service
- [ ] Four MCP tools: list, push, pull, delete
- [ ] Expiration, cleanup, and guarded history compaction
- [ ] File-browser UI, hardened previews, custom domain
