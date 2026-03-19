"""LangSmith tracing integration (optional dependency).

When langsmith is installed and configured, benchmark runs and evaluations
are automatically traced. When not available, this module provides no-op
decorators with zero overhead.
"""

from __future__ import annotations

import functools
import logging
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])

_langsmith_available = False

try:
    from langsmith import traceable as _traceable

    _langsmith_available = True
    logger.debug("LangSmith tracing enabled")
except ImportError:
    _traceable = None  # type: ignore[assignment]


def traceable(name: str | None = None, **kwargs: Any) -> Callable[[F], F]:
    """Decorator that traces a function with LangSmith when available.

    Falls back to a no-op decorator when langsmith is not installed.
    """
    if _langsmith_available and _traceable is not None:
        return _traceable(name=name, **kwargs)  # type: ignore[return-value]

    def _noop(fn: F) -> F:
        return fn

    return _noop


def trace_benchmark(fn: F) -> F:
    """Convenience decorator for tracing benchmark runs."""
    if _langsmith_available and _traceable is not None:
        return _traceable(name="agentbench.run_benchmark", run_type="chain")(fn)  # type: ignore[return-value]
    return fn


def is_tracing_enabled() -> bool:
    """Check if LangSmith tracing is available."""
    return _langsmith_available
