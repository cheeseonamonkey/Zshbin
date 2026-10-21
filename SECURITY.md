# Security

**Bootstrap only — not a secure pastebin yet.** The legacy CLI accepts *plaintext* uploads only with explicit `--public`. Encryption, expiration, restricted sharing, and history rewriting are not implemented. Do not upload passwords, private keys, or confidential files.

Authentication is delegated to GitHub CLI (`gh auth`) or environment-supplied tokens. Zshbin config stores only the target repository. GitHub Contents write permission is repository-wide, not path-scoped; use a separate repository for uploaded data, **not the source repository**. There is no browser upload or hosted MCP server yet.

Deleted data can remain in Git history and external clones indefinitely. Future encryption cannot retroactively protect plaintext previously uploaded.

For a sensitive issue, use [private vulnerability reporting](https://github.com/cheeseonamonkey/Zshbin/security/advisories/new) if enabled. Avoid posting exploit details publicly.
