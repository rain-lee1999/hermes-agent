"""Tests for hermes_cli.update_source helpers."""

from hermes_cli.update_source import resolve_local_update_source_repo


def test_resolve_local_update_source_repo_prefers_sibling_update_checkout(tmp_path):
    update_repo = tmp_path / "hermes-agent-update"
    update_repo.mkdir()
    (update_repo / ".git").mkdir()

    source_repo = tmp_path / "hermes-agent"
    source_repo.mkdir()
    (source_repo / ".git").mkdir()

    assert resolve_local_update_source_repo(update_repo) == source_repo.resolve()


def test_resolve_local_update_source_repo_honors_env_override(tmp_path, monkeypatch):
    update_repo = tmp_path / "hermes-agent-update"
    update_repo.mkdir()
    (update_repo / ".git").mkdir()

    env_source = tmp_path / "custom-source"
    env_source.mkdir()
    (env_source / ".git").mkdir()

    monkeypatch.setenv("HERMES_UPDATE_SOURCE_REPO", str(env_source))

    assert resolve_local_update_source_repo(update_repo) == env_source.resolve()
