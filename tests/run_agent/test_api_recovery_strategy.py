from __future__ import annotations

import time
from types import SimpleNamespace

import pytest


def _bare_agent():
    from run_agent import AIAgent

    agent = AIAgent.__new__(AIAgent)
    agent.provider = "openai-codex"
    agent.model = "gpt-5.5"
    agent.api_mode = "chat_completions"
    agent.base_url = "https://api.openai.com/v1"
    agent._base_url = agent.base_url
    agent._base_url_lower = agent.base_url.lower()
    agent._base_url_hostname = "api.openai.com"
    agent._interrupt_requested = False
    agent._non_stream_stale_timeout_count = 0
    agent.log_prefix = ""
    agent._touch_activity = lambda message: None
    agent._emit_status = lambda message: None
    agent._close_request_openai_client = lambda client, reason: None
    return agent


class _FakeStream:
    response = None

    def __init__(self, events):
        self._events = events

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def __iter__(self):
        return iter(self._events)

    def get_final_response(self):
        return SimpleNamespace(output=[])


class _FakeResponses:
    def __init__(self, events):
        self._events = events

    def stream(self, **kwargs):
        return _FakeStream(self._events)


class _FakeCodexClient:
    def __init__(self, events):
        self.responses = _FakeResponses(events)


class _SlowChatClient:
    class _Chat:
        class _Completions:
            def __init__(self, delay, response):
                self._delay = delay
                self._response = response

            def create(self, **kwargs):
                time.sleep(self._delay)
                return self._response

        def __init__(self, delay, response):
            self.completions = self._Completions(delay, response)

    def __init__(self, delay, response):
        self.chat = self._Chat(delay, response)


def test_codex_stream_marks_provider_activity_for_reasoning_and_text_events():
    agent = _bare_agent()
    agent.api_mode = "codex_responses"
    agent._fire_stream_delta = lambda text: None
    agent._fire_reasoning_delta = lambda text: None
    agent._codex_streamed_text_parts = []

    events = [
        SimpleNamespace(type="response.reasoning.delta", delta="thinking"),
        SimpleNamespace(type="response.output_text.delta", delta="hello"),
    ]
    activity = []

    agent._run_codex_stream(
        {"model": "gpt-5.5", "input": "hello"},
        client=_FakeCodexClient(events),
        on_stream_activity=lambda: activity.append("tick"),
    )

    assert len(activity) == 2


def test_non_streaming_stale_timeout_increments_count_without_resetting_on_error():
    agent = _bare_agent()
    agent._compute_non_stream_stale_timeout = lambda api_kwargs: 0.01
    agent._create_request_openai_client = lambda reason, api_kwargs: _SlowChatClient(
        2.5, SimpleNamespace(id="late")
    )

    with pytest.raises(TimeoutError):
        agent._interruptible_api_call({"model": "gpt-5.5", "messages": []})

    assert agent._non_stream_stale_timeout_count == 1


def test_successful_non_streaming_api_call_resets_stale_timeout_count():
    agent = _bare_agent()
    response = SimpleNamespace(id="ok")
    agent._non_stream_stale_timeout_count = 3
    agent._compute_non_stream_stale_timeout = lambda api_kwargs: 10.0
    agent._create_request_openai_client = lambda reason, api_kwargs: _SlowChatClient(0.0, response)

    assert agent._interruptible_api_call({"model": "gpt-5.5", "messages": []}) is response
    assert agent._non_stream_stale_timeout_count == 0


def test_visible_transport_failure_status_labels_are_emitted():
    from agent.error_classifier import ClassifiedError, FailoverReason

    agent = _bare_agent()
    emitted = []
    agent._emit_status = emitted.append
    classified = ClassifiedError(reason=FailoverReason.timeout, retryable=True)

    agent._emit_visible_transport_failure_status(TimeoutError("stale"), classified, recovered=None)
    agent._emit_visible_transport_failure_status(TimeoutError("stale"), classified, recovered=True)
    agent._emit_visible_transport_failure_status(TimeoutError("stale"), classified, recovered=False)

    joined = "\n".join(emitted)
    assert "transport_failure[recovery_pending]" in joined
    assert "transport_failure[recovered]" in joined
    assert "transport_failure[recovery_failed]" in joined
    assert "visible_transport_auto_recovery" in joined
