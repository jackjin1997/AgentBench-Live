"""Tests for LangSmith tracing integration."""

from __future__ import annotations

from unittest.mock import patch

from agentbench.tracing import is_tracing_enabled, trace_benchmark, traceable


class TestTracingNotAvailable:
    @patch("agentbench.tracing._langsmith_available", False)
    def test_is_tracing_disabled(self):
        assert is_tracing_enabled() is False

    @patch("agentbench.tracing._langsmith_available", False)
    @patch("agentbench.tracing._traceable", None)
    def test_traceable_noop(self):
        @traceable(name="test")
        def my_func(x):
            return x + 1

        assert my_func(1) == 2

    @patch("agentbench.tracing._langsmith_available", False)
    @patch("agentbench.tracing._traceable", None)
    def test_trace_benchmark_noop(self):
        @trace_benchmark
        def my_benchmark():
            return "result"

        assert my_benchmark() == "result"


class TestTracingAvailable:
    def test_is_tracing_reflects_availability(self):
        # This test checks the actual state — may be True or False
        result = is_tracing_enabled()
        assert isinstance(result, bool)

    @patch("agentbench.tracing._langsmith_available", True)
    def test_traceable_with_mock(self):
        mock_traceable = lambda name=None, **kw: lambda fn: fn

        with patch("agentbench.tracing._traceable", mock_traceable):
            @traceable(name="test")
            def my_func(x):
                return x * 2

            assert my_func(3) == 6
