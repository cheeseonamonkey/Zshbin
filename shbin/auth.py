"""Use GitHub CLI authentication; never persist tokens in local project config."""

import json
import os
import re
import shutil
import subprocess
import tempfile

from platformdirs import user_config_path
from rich import print
from rich.prompt import Prompt

CONFIG_PATH = user_config_path("zshbin") / "config.json"


def load_config():
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_config(cfg):
    """Save only the target repo; never write credentials to disk."""
    repo = cfg.get("repo")
    if not isinstance(repo, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise ValueError("Repository must have owner/name format")
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temporary = tempfile.mkstemp(prefix=".config-", dir=CONFIG_PATH.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            json.dump({"repo": repo}, file)
        os.chmod(temporary, 0o600)
        os.replace(temporary, CONFIG_PATH)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def get_token():
    for name in ("ZSHBIN_GITHUB_TOKEN", "GH_TOKEN", "GITHUB_TOKEN", "SHBIN_GITHUB_TOKEN"):
        if token := os.environ.get(name):
            return token
    try:
        result = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=False, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def do_auth():
    if not shutil.which("gh"):
        raise SystemExit("Install GitHub CLI (gh), or set ZSHBIN_GITHUB_TOKEN and ZSHBIN_REPO.")
    if not get_token():
        subprocess.run(["gh", "auth", "login"], check=True)
    if not get_token():
        raise SystemExit("GitHub authentication failed.")
    repo = Prompt.ask("Target pastebin repository (owner/name)")
    save_config({"repo": repo})
    print("[green]✓[/green] Repository saved; access token stays managed by GitHub CLI.")
