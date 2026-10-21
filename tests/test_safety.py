import pytest
from docopt import DocoptExit

from shbin import main
from shbin.auth import get_token, load_config, save_config


def test_plaintext_requires_public(mocker):
    lookup = mocker.patch("shbin.get_repo_and_user")
    with pytest.raises(DocoptExit, match="--public"):
        main(["secret.txt"])
    lookup.assert_not_called()


def test_env_token_preferred(monkeypatch):
    monkeypatch.setenv("ZSHBIN_GITHUB_TOKEN", "env-token")
    assert get_token() == "env-token"


def test_config_omits_all_secrets(monkeypatch, tmp_path):
    import shbin.auth as auth

    monkeypatch.setattr(auth, "CONFIG_PATH", tmp_path / "config.json")
    save_config({"repo": "owner/data", "token": "never-write", "password": "never-write"})
    assert load_config() == {"repo": "owner/data"}
    assert auth.CONFIG_PATH.stat().st_mode & 0o777 == 0o600


@pytest.mark.parametrize("repo", ["../../../etc", "missing-slash", "owner/../../repo", ""])
def test_bad_repo_rejected(monkeypatch, tmp_path, repo):
    import shbin.auth as auth

    monkeypatch.setattr(auth, "CONFIG_PATH", tmp_path / "config.json")
    with pytest.raises(ValueError):
        save_config({"repo": repo})
