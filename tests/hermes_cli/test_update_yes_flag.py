"""Tests for `hermes update --yes / -y`.

Covers:
  1. argparse parses the flag
  2. Update no longer mutates config/.env during the main code-update flow
  3. Autostash restore prompt is auto-answered (prompt_for_restore == False, no
     input() call) and the stash is applied automatically
"""

import subprocess
from types import SimpleNamespace
from unittest.mock import patch

from hermes_cli.main import cmd_update


def _make_run_side_effect(
    branch="main", verify_ok=True, commit_count="1", dirty=False
):
    """Minimal subprocess.run side_effect for the update flow."""

    def side_effect(cmd, **kwargs):
        joined = " ".join(str(c) for c in cmd)

        if "rev-parse" in joined and "--abbrev-ref" in joined:
            return subprocess.CompletedProcess(cmd, 0, stdout=f"{branch}\n", stderr="")
        if "rev-parse" in joined and "--verify" in joined:
            return subprocess.CompletedProcess(
                cmd, 0 if verify_ok else 128, stdout="", stderr=""
            )
        if "rev-list" in joined:
            return subprocess.CompletedProcess(
                cmd, 0, stdout=f"{commit_count}\n", stderr=""
            )
        # `git status --porcelain` for dirty-tree detection during autostash.
        if "status" in joined and "--porcelain" in joined:
            out = " M hermes_cli/main.py\n" if dirty else ""
            return subprocess.CompletedProcess(cmd, 0, stdout=out, stderr="")
        # `git stash list` — return a stash ref when dirty (so _stash_local_changes
        # gets something to return). _stash_local_changes_if_needed is what we
        # actually patch in tests that exercise restore, so this is a catch-all.
        if "stash" in joined and "list" in joined:
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    return side_effect


class TestUpdateConfigMigrationRemovedFromMainFlow:
    """`hermes update` no longer mutates config/.env during code update."""

    @patch("hermes_cli.config.check_config_version", return_value=(1, 2))
    @patch("hermes_cli.config.get_missing_config_fields", return_value=[])
    @patch("hermes_cli.config.get_missing_env_vars", return_value=["NEW_KEY"])
    @patch("shutil.which", return_value=None)
    @patch("subprocess.run")
    def test_yes_does_not_auto_migrate_config(
        self,
        mock_run,
        _mock_which,
        _mock_missing_env,
        _mock_missing_cfg,
        _mock_version,
        capsys,
    ):
        mock_run.side_effect = _make_run_side_effect(
            branch="main", verify_ok=True, commit_count="1"
        )

        args = SimpleNamespace(yes=True)

        with patch("builtins.input") as mock_input:
            cmd_update(args)
            # Update no longer prompts for config migration.
            mock_input.assert_not_called()

        out = capsys.readouterr().out
        assert "Run 'hermes config migrate' later if you want to apply them." in out
        assert "--yes: auto-applying config migration" not in out
        assert "Would you like to configure them now?" not in out

    @patch("hermes_cli.config.check_config_version", return_value=(1, 2))
    @patch("hermes_cli.config.get_missing_config_fields", return_value=[])
    @patch("hermes_cli.config.get_missing_env_vars", return_value=["NEW_KEY"])
    @patch("shutil.which", return_value=None)
    @patch("subprocess.run")
    def test_without_yes_still_does_not_prompt_for_config_migration(
        self,
        mock_run,
        _mock_which,
        _mock_missing_env,
        _mock_missing_cfg,
        _mock_version,
        capsys,
    ):
        """Regression guard: config migration is reported, not interactive."""
        mock_run.side_effect = _make_run_side_effect(
            branch="main", verify_ok=True, commit_count="1"
        )

        args = SimpleNamespace(yes=False)

        with patch("builtins.input") as mock_input:
            cmd_update(args)
            mock_input.assert_not_called()

        out = capsys.readouterr().out
        assert "Run 'hermes config migrate' later if you want to apply them." in out


class TestUpdateYesStashRestore:
    """--yes auto-restores the pre-update autostash without prompting."""

    @patch("hermes_cli.main._restore_stashed_changes")
    @patch(
        "hermes_cli.main._stash_local_changes_if_needed",
        return_value="stash@{0}",
    )
    @patch("hermes_cli.config.check_config_version", return_value=(1, 1))
    @patch("hermes_cli.config.get_missing_config_fields", return_value=[])
    @patch("hermes_cli.config.get_missing_env_vars", return_value=[])
    @patch("shutil.which", return_value=None)
    @patch("subprocess.run")
    def test_yes_restores_stash_without_prompting(
        self,
        mock_run,
        _mock_which,
        _mock_missing_env,
        _mock_missing_cfg,
        _mock_version,
        _mock_stash,
        mock_restore,
        capsys,
    ):
        # Not on main → cmd_update switches to main → autostash fires.
        mock_run.side_effect = _make_run_side_effect(
            branch="feature-branch", verify_ok=True, commit_count="1", dirty=True
        )

        args = SimpleNamespace(yes=True)

        cmd_update(args)

        # _restore_stashed_changes was called, and called with prompt_user=False
        # every time (so the user never sees "Restore local changes now?").
        assert mock_restore.called
        for call in mock_restore.call_args_list:
            assert call.kwargs.get("prompt_user") is False, (
                f"Expected prompt_user=False under --yes, got {call.kwargs}"
            )
