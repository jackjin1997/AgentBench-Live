import json
import pytest
from pathlib import Path

from config.local import LocalConfigLoader
from config.schema import AppConfig


@pytest.fixture()
def config_file(tmp_path: Path) -> Path:
    """Write a minimal valid config JSON and return its path."""
    data = {
        "app_name": "test-app",
        "debug": True,
        "log_level": "DEBUG",
        "max_connections": 50,
        "api_key": "secret-key-123",
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


class TestLocalConfigLoader:
    """Tests for LocalConfigLoader."""

    def test_load_valid_config(self, config_file: Path) -> None:
        loader = LocalConfigLoader(str(config_file))
        cfg = loader.load()

        assert isinstance(cfg, AppConfig)
        assert cfg.app_name == "test-app"
        assert cfg.debug is True
        assert cfg.log_level == "DEBUG"
        assert cfg.max_connections == 50
        assert cfg.api_key == "secret-key-123"

    def test_load_minimal_config(self, tmp_path: Path) -> None:
        """Only the required field (app_name) is present; defaults apply."""
        data = {"app_name": "minimal"}
        path = tmp_path / "minimal.json"
        path.write_text(json.dumps(data), encoding="utf-8")

        cfg = LocalConfigLoader(str(path)).load()

        assert cfg.app_name == "minimal"
        assert cfg.debug is False
        assert cfg.log_level == "INFO"
        assert cfg.max_connections == 100
        assert cfg.api_key == ""

    def test_load_missing_file(self, tmp_path: Path) -> None:
        loader = LocalConfigLoader(str(tmp_path / "nonexistent.json"))
        with pytest.raises(FileNotFoundError):
            loader.load()

    def test_load_invalid_json(self, tmp_path: Path) -> None:
        path = tmp_path / "bad.json"
        path.write_text("not json at all", encoding="utf-8")

        loader = LocalConfigLoader(str(path))
        with pytest.raises(json.JSONDecodeError):
            loader.load()

    def test_load_schema_violation(self, tmp_path: Path) -> None:
        """JSON is valid but missing required 'app_name' field."""
        path = tmp_path / "incomplete.json"
        path.write_text(json.dumps({"debug": True}), encoding="utf-8")

        loader = LocalConfigLoader(str(path))
        with pytest.raises(Exception):  # pydantic ValidationError
            loader.load()
