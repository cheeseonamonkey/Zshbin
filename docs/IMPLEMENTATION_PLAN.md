# Zshbin — Hardened implementation plan

**Scope:** public standalone source; static GitHub Pages UI; separate public ciphertext storage; authenticated writes; encrypted-by-default sharing; optional public plaintext, expiration, four MCP tools, and guarded history cleanup. No always-on backend unless restricted key release or web upload is enabled.

## Decisions and security invariants

- Public repo does **not** imply that uploaded files should be readable. Default to encryption once implemented. Until then, plain upload requires explicit `--public`.
- A random per-file salt is public; a server-held secret is a **pepper or key share**, not a salt. Never use a partial plaintext file as a salt, or concatenate passwords and file bytes to invent an encryption algorithm.
- Do not keep complete decrypting key material in GitHub, Actions logs, CI artifacts, website JavaScript, metadata manifests, or publicly accessible endpoints.
- Authenticate users with GitHub; *separately* authorize write/decrypt/delete. Public GitHub identity is not automatically permission to upload.
- No guaranteed secure erasure from public Git history, forks, caches, copies, or already disclosed keys. Expires and delete mean removal from active app/storage, not guaranteed destruction.

## Phases

### 1. Bootstrap [done]
- Migrate the maintained Python core + tests into a new standalone repository; retain ShipHero MIT attribution.
- Independent `zshbin` package/CLI (old import module temporarily remains `shbin`).
- Eliminate inherited upstream OAuth client ID; use `gh auth` or scoped environment token. Never save the token in project config.
- Fail closed on implicit plaintext upload; `--public` required until encryption arrives.
- Static Pages landing page, read-only CI, no fork-only PyPI release automation.

### 2. Isolate data and make uploads atomic
- **Recommended:** separate public data repository, because a GitHub Contents write token cannot be restricted to just `data/` or a branch. Or implement a narrow write broker.
- Opaque random ID per file; immutable object content; versioned manifest entry with digest, size, created/expires UTC, cipher metadata, content type and nonsensitive display name.
- Validate paths, namespace, maximum bytes, metadata, content type; never let file uploads overwrite workflows or application code.
- Commit object + manifest atomically via Git tree/commit/ref compare-and-swap. Bound conflict retries; reject tampered manifests; ensure no partial live entries. Use SHA-256 for integrity.
- Migrate legacy API and route all CLI/MCP/UI operations through shared storage core.

### 3. Strong encryption and key management
- Generate fresh independent random 256-bit DEK per file. Encrypt with a maintained AEAD implementation: AES-256-GCM or XChaCha20-Poly1305, with strictly unique nonce, authenticated versioned envelope and associated metadata.
- Recipient mode: OpenPGP-compatible public-key wrapping of DEK, or age/X25519; use established implementations, test interoperability, and never upload private keys.
- Optional password factor: Argon2id password-based KEK, **random per-file salt** and bounded parameters; wrap DEK with authenticated key wrap. A password protecting a PGP private key is not necessarily an independent cryptographic factor.
- Optional extra server factor: authenticated key broker with high-entropy secret/key share, used through audited multi-layer key wrapping or all-of-N recovery, not homemade hash concatenation. GitHub Actions Secrets can't serve interactive web requests. Manage key ID, rotation, recovery policy, rate limits, audit trail.
- Verify ciphertext and integrity *before* returning plaintext; never leak cryptographic failure details or decrypt in CI. Test CLI↔browser known-answer vectors, wrong keys, tampered headers, nonce reuse and lost-factor recovery.

### 4. CLI and MCP
- Three primary operations plus deletion: `list`, `push`, `pull`, `delete`; local stdio MCP first.
- Default read-only agent permissions; require explicit opt-in for writes/deletes; strict local root directory allowlist and max sizes; never inadvertently expose a decrypted secret in MCP response or logs.
- `push`: bytes/streams, metadata, optional expiration, recipients and encryption policy. `pull`: digest-verified read/decrypt; controlled output. `list`: prefix, cursor, limit, expiration. `delete`: immutable file ID, validated scope, no recursive MCP deletion by default.
- Browser uploads later via GitHub OAuth/GitHub App and trusted broker: identity verification, CSRF protections, state/PKCE where applicable, secure session, server-side allowlist, short-lived credentials. Never embed write tokens in Pages.

### 5. Expiration and deletion
- Optional `--expire 30m|12h|7d|ISO8601`; canonical UTC `expires_at`. Optional no-expiry default.
- Exclude expired entries immediately from listings/viewer; hourly Actions cleanup is best-effort and may be delayed or disabled. Offer manual dispatch and overdue metrics.
- Remove active objects/manifest references atomically; tombstone IDs to prevent accidental resurrection. Deleted plaintext in Git remains exposed to anyone with historical access.
- Start with manual dry-run history pruning on **data repo only**. Verify every retained object digest, ensure no concurrent updates, and use lease-guarded ref swaps. Enable weekly compaction only after tests and dry-run success.
- No long-lived plaintext backups. Document inability to erase clones, caches, prior shares and ciphertext already downloaded.

### 6. Pages application
- Build static file browser with bounded manifest search, filtering, safe text/Markdown/image previews and download. Escaping/sandboxing untrusted HTML/SVG; no script execution on app origin. Strict CSP, no analytics leaking fragments.
- Decrypt in browser with Web Crypto or audited compatible library; share key in URL fragment *only* with clear bearer-link warnings. No persistence of private keys in localStorage.
- Custom domain later; account for project Pages subpath before migration.

### 7. CI, quality, recovery
- Read-only `GITHUB_TOKEN` by default, scoped Pages job gets `pages:write` + `id-token:write`, cleanup writer only on trusted events. Review/pin third-party Action SHAs.
- Avoid executing user-uploaded files or allowing `pull_request_target` scripts. Credential leak scans, dependency audit, positive/negative crypto cases, race/conflict tests, interrupted uploads and Git history restoration simulation.
- Confirm Pages settings manually, check deployment URLs, verify privacy/secret boundaries, run full regression before declaring launch.

## Deferred intentionally

Hosted remote MCP, password/key broker, GitHub App installation, custom domain, background queue, automatic force-push compaction, web uploads and secret-requiring CI workflows. These need a vetted storage/auth boundary first.
