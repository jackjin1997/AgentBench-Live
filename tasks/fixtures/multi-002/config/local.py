import json
from pathlib import Path

from config.schema import AppConfig


class LocalConfigLoader:
    """Loads application configuration from a local JSON file."""

    def __init__(self, path: str) -> None:
        self._path = Path(path)

    def load(self) -> AppConfig:
        """Read the JSON file and return a validated AppConfig.

        Raises:
            FileNotFoundError: If the config file does not exist.
            json.JSONDecodeError: If the file is not valid JSON.
            pydantic.ValidationError: If the JSON does not match the schema.
        """
        text = self._path.read_text(encoding="utf-8")
        data = json.loads(text)
        return AppConfig(**data)
