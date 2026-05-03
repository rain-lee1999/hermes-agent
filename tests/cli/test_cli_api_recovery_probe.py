from __future__ import annotations

import queue

from tests.cli.test_cli_init import _make_cli


def test_cli_does_not_invent_question_probe_after_visible_recoverable_transport_failure():
    cli = _make_cli()
    cli._pending_input = queue.Queue()

    cli._on_agent_status(
        "lifecycle",
        "transport_failure[recovery_pending] visible_transport_auto_recovery reason=timeout",
    )

    assert cli._queue_auto_recovery_probe_if_needed(pending_message=None) is False
    assert cli._pending_input.empty()
    assert cli._auto_recovery_probe_pending is False


def test_cli_does_not_auto_probe_when_user_interrupt_message_exists():
    cli = _make_cli()
    cli._pending_input = queue.Queue()

    cli._on_agent_status(
        "lifecycle",
        "transport_failure[recovery_pending] visible_transport_auto_recovery reason=timeout",
    )

    assert cli._queue_auto_recovery_probe_if_needed(pending_message="user said stop") is False
    assert cli._pending_input.empty()
