"""Tests for cmd_update — branch fallback when remote branch doesn't exist."""

import subprocess
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from hermes_cli.main import cmd_update, PROJECT_ROOT
import hermes_cli.main as hermes_main


def _make_run_side_effect(branch="main", verify_ok=True, commit_count="0"):
    """Build a side_effect function for subprocess.run that simulates git commands."""

    def side_effect(cmd, **kwargs):
        joined = " ".join(str(c) for c in cmd)

        # git rev-parse --abbrev-ref HEAD  (get current branch)
        if "rev-parse" in joined and "--abbrev-ref" in joined:
            return subprocess.CompletedProcess(cmd, 0, stdout=f"{branch}\n", stderr="")

        # git rev-parse --verify origin/{branch}  (check remote branch exists)
        if "rev-parse" in joined and "--verify" in joined:
            rc = 0 if verify_ok else 128
            return subprocess.CompletedProcess(cmd, rc, stdout="", stderr="")

        # git rev-list HEAD..origin/{branch} --count
        if "rev-list" in joined:
            return subprocess.CompletedProcess(cmd, 0, stdout=f"{commit_count}\n", stderr="")

        # Fallback: return a successful CompletedProcess with empty stdout
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    return side_effect


@pytest.fixture
def mock_args():
    return SimpleNamespace()


class TestCmdUpdateBranchFallback:
    """cmd_update falls back to main when current branch has no remote counterpart."""

    @patch("shutil.which", return_value=None)
    @patch("subprocess.run")
    def test_update_falls_back_to_main_when_branch_not_on_remote(
        self, mock_run, _mock_which, mock_args, monkeypatch, capsys
    ):
        monkeypatch.setattr(hermes_main, "resolve_local_update_source_repo", lambda project_root: None)
        mock_run.side_effect = _make_run_side_effect(
            branch="fix/stoicneko", verify_ok=False, commit_count="3"
        )

        cmd_update(mock_args)

        commands = [" ".join(str(a) for a in c.args[0]) for c in mock_run.call_args_list]

        # rev-list should use origin/main, not origin/fix/stoicneko
        rev_list_cmds = [c for c in commands if "rev-list" in c]
        assert len(rev_list_cmds) == 1
        assert "origin/main" in rev_list_cmds[0]
        assert "origin/fix/stoicneko" not in rev_list_cmds[0]

        # pull should use main, not fix/stoicneko
        pull_cmds = [c for c in commands if "pull" in c]
        assert len(pull_cmds) == 1
        assert "main" in pull_cmds[0]

    @patch("shutil.which", return_value=None)
    @patch("subprocess.run")
    def test_update_uses_current_branch_when_on_remote(
        self, mock_run, _mock_which, mock_args, monkeypatch, capsys
    ):
        monkeypatch.setattr(hermes_main, "resolve_local_update_source_repo", lambda project_root: None)
        mock_run.side_effect = _make_run_side_effect(
            branch="main", verify_ok=True, commit_count="2"
        )

        cmd_update(mock_args)

        commands = [" ".join(str(a) for a in c.args[0]) for c in mock_run.call_args_list]

        rev_list_cmds = [c for c in commands if "rev-list" in c]
        assert len(rev_list_cmds) == 1
        assert "origin/main" in rev_list_cmds[0]

        pull_cmds = [c for c in commands if "pull" in c]
        assert len(pull_cmds) == 1
        assert "main" in pull_cmds[0]

    @patch("shutil.which", return_value=None)
    def test_update_prefers_local_source_checkout(self, _mock_which, mock_args, tmp_path, monkeypatch, capsys):
        local_source = tmp_path / "hermes-agent-source"
        local_source.mkdir()
        (local_source / ".git").mkdir()

        monkeypatch.setattr(hermes_main, "resolve_local_update_source_repo", lambda project_root: local_source)

        recorded = []

        def fake_run(cmd, **kwargs):
            recorded.append(cmd)
            if cmd == ["git", "fetch", "--quiet", str(local_source), "main"]:
                return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")
            if cmd == ["git", "rev-parse", "--abbrev-ref", "HEAD"]:
                return subprocess.CompletedProcess(cmd, 0, stdout="main\n", stderr="")
            if cmd == ["git", "rev-list", "HEAD..FETCH_HEAD", "--count"]:
                return subprocess.CompletedProcess(cmd, 0, stdout="1\n", stderr="")
            if cmd == ["git", "pull", "--ff-only", str(local_source), "main"]:
                return subprocess.CompletedProcess(cmd, 0, stdout="Updating\n", stderr="")
            if cmd == ["git", "status", "--porcelain"]:
                return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

        monkeypatch.setattr(hermes_main.subprocess, "run", fake_run)

        cmd_update(mock_args)

        commands = [" ".join(str(a) for a in cmd) for cmd in recorded]
        assert any(str(local_source) in cmd for cmd in commands if "fetch" in cmd)
        assert any(str(local_source) in cmd for cmd in commands if "pull" in cmd)
        assert not any("origin" in cmd for cmd in commands if "fetch" in cmd)
        out = capsys.readouterr().out
        assert "local source checkout" in out

    @patch("shutil.which", return_value=None)
    @patch("subprocess.run")
    def test_update_already_up_to_date(
        self, mock_run, _mock_which, mock_args, capsys
    ):
        mock_run.side_effect = _make_run_side_effect(
            branch="main", verify_ok=True, commit_count="0"
        )

        cmd_update(mock_args)

        captured = capsys.readouterr()
        assert "Already up to date!" in captured.out

        # Should NOT have called pull
        commands = [" ".join(str(a) for a in c.args[0]) for c in mock_run.call_args_list]
        pull_cmds = [c for c in commands if "pull" in c]
        assert len(pull_cmds) == 0

    @patch("hermes_cli.profiles.seed_profile_skills")
    @patch("hermes_cli.profiles.list_profiles", return_value=[])
    @patch("hermes_cli.profiles.get_active_profile_name", return_value="default")
    @patch("tools.skills_sync.sync_skills")
    @patch("shutil.which", return_value=None)
    @patch("subprocess.run")
    def test_update_skills_sync_is_skipped_by_default(
        self,
        mock_run,
        _mock_which,
        mock_sync_skills,
        _mock_active_profile,
        _mock_list_profiles,
        _mock_seed_profile_skills,
        mock_args,
        capsys,
    ):
        mock_run.side_effect = _make_run_side_effect(
            branch="main", verify_ok=True, commit_count="1"
        )
        mock_sync_skills.return_value = {
            "copied": [],
            "updated": [],
            "skipped": 0,
            "user_modified": [],
            "cleaned": [],
            "total_bundled": 0,
        }

        cmd_update(mock_args)

        mock_sync_skills.assert_not_called()
        _mock_seed_profile_skills.assert_not_called()
        out = capsys.readouterr().out
        assert "Bundled skills sync skipped (use --sync-skills to enable)" in out

    @patch("hermes_cli.profiles.seed_profile_skills")
    @patch("hermes_cli.profiles.list_profiles", return_value=[])
    @patch("hermes_cli.profiles.get_active_profile_name", return_value="default")
    @patch("tools.skills_sync.sync_skills")
    @patch("shutil.which", return_value=None)
    @patch("subprocess.run")
    def test_update_sync_skills_flag_runs_skill_sync(
        self,
        mock_run,
        _mock_which,
        mock_sync_skills,
        _mock_active_profile,
        _mock_list_profiles,
        _mock_seed_profile_skills,
        mock_args,
        capsys,
    ):
        mock_run.side_effect = _make_run_side_effect(
            branch="main", verify_ok=True, commit_count="1"
        )
        mock_sync_skills.return_value = {
            "copied": ["alpha"],
            "updated": [],
            "skipped": 0,
            "user_modified": [],
            "cleaned": [],
            "total_bundled": 1,
        }

        args = SimpleNamespace(sync_skills=True)
        cmd_update(args)

        mock_sync_skills.assert_called_once_with(quiet=True)
        _mock_seed_profile_skills.assert_not_called()
        out = capsys.readouterr().out
        assert "Syncing bundled skills" in out
        assert "alpha" in out

    @patch("hermes_cli.main._build_web_ui")
    @patch("hermes_cli.main._update_node_dependencies")
    @patch("hermes_cli.main._install_python_dependencies_with_optional_fallback")
    @patch("hermes_cli.main._sync_with_upstream_if_needed")
    @patch("hermes_cli.main._run_pre_update_backup")
    @patch("hermes_cli.main._clear_bytecode_cache", return_value=0)
    @patch("shutil.which", return_value="/usr/bin/uv")
    @patch("subprocess.run")
    def test_simple_update_skips_heavy_post_update_work(
        self,
        mock_run,
        _mock_which,
        _mock_clear_pyc,
        mock_backup,
        mock_upstream_sync,
        mock_install_python,
        mock_update_node,
        mock_build_web,
        monkeypatch,
        capsys,
    ):
        monkeypatch.setattr(hermes_main, "resolve_local_update_source_repo", lambda project_root: None)
        mock_run.side_effect = _make_run_side_effect(
            branch="main", verify_ok=True, commit_count="1"
        )

        cmd_update(SimpleNamespace(simple=True))

        mock_backup.assert_not_called()
        mock_install_python.assert_not_called()
        mock_update_node.assert_not_called()
        mock_build_web.assert_not_called()
        mock_upstream_sync.assert_not_called()
        out = capsys.readouterr().out
        assert "Code updated (simple mode)" in out
        assert "dependency reinstall" in out

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_update_refreshes_repo_and_tui_node_dependencies(
        self, mock_run, mock_which, mock_args, monkeypatch
    ):
        monkeypatch.setattr(hermes_main, "resolve_local_update_source_repo", lambda project_root: None)
        monkeypatch.setattr(hermes_main, "_web_ui_build_needed", lambda web_dir: True)
        mock_which.side_effect = {"uv": "/usr/bin/uv", "npm": "/usr/bin/npm"}.get
        mock_run.side_effect = _make_run_side_effect(
            branch="main", verify_ok=True, commit_count="1"
        )

        cmd_update(mock_args)

        npm_calls = [
            (call.args[0], call.kwargs.get("cwd"))
            for call in mock_run.call_args_list
            if call.args and call.args[0][0] == "/usr/bin/npm"
        ]

        # cmd_update runs npm commands in three locations:
        #   1. repo root  — slash-command / TUI bridge deps
        #   2. ui-tui/    — Ink TUI deps
        #   3. web/       — install + "npm run build" for the web frontend
        full_flags = [
            "/usr/bin/npm",
            "ci",
            "--silent",
            "--no-fund",
            "--no-audit",
            "--progress=false",
        ]
        assert npm_calls == [
            (full_flags, PROJECT_ROOT),
            (full_flags, PROJECT_ROOT / "ui-tui"),
            (["/usr/bin/npm", "ci", "--silent"], PROJECT_ROOT / "web"),
            (["/usr/bin/npm", "run", "build"], PROJECT_ROOT / "web"),
        ]

    def test_update_non_interactive_reports_migration_available_but_skips_prompt(self, mock_args, capsys):
        """When stdin/stdout aren't TTYs, update reports config drift without prompting."""
        with patch("shutil.which", return_value=None), patch(
            "subprocess.run"
        ) as mock_run, patch("builtins.input") as mock_input, patch(
            "hermes_cli.config.get_missing_env_vars", return_value=["MISSING_KEY"]
        ), patch("hermes_cli.config.get_missing_config_fields", return_value=[]), patch(
            "hermes_cli.config.check_config_version", return_value=(1, 2)
        ), patch("hermes_cli.main.sys") as mock_sys:
            mock_sys.stdin.isatty.return_value = False
            mock_sys.stdout.isatty.return_value = False
            mock_run.side_effect = _make_run_side_effect(
                branch="main", verify_ok=True, commit_count="1"
            )

            cmd_update(mock_args)

            mock_input.assert_not_called()
            captured = capsys.readouterr()
            assert "Run 'hermes config migrate' later if you want to apply them." in captured.out
