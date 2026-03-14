from __future__ import annotations

from typing import Protocol

from config.schema import AppConfig


class ConfigLoader(Protocol):
    """Protocol that all config loaders must satisfy."""

    def load(self) -> AppConfig: ...


class ConfigManager:
    """Manages multiple configuration loaders and returns the first successful result.

    Loaders are tried in registration order. The first loader that returns
    a valid ``AppConfig`` wins; if a loader raises an exception it is
    silently skipped and the next loader is tried.
    """

    def __init__(self) -> None:
        self._loaders: list[ConfigLoader] = []

    def register_loader(self, loader: ConfigLoader) -> None:
        """Append *loader* to the end of the loader chain."""
        self._loaders.append(loader)

    def load(self) -> AppConfig:
        """Try each registered loader in order and return the first success.

        Raises:
            RuntimeError: If no loader is registered or all loaders fail.
        """
        if not self._loaders:
            raise RuntimeError("No config loaders registered")

        errors: list[Exception] = []
        for loader in self._loaders:
            try:
                return loader.load()
            except Exception as exc:  # noqa: BLE001
                errors.append(exc)

        raise RuntimeError(
            f"All {len(errors)} config loader(s) failed. "
            f"Last error: {errors[-1]}"
        )
