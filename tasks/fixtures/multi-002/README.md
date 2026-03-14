# Config System

A pluggable configuration loading system for a CLI tool.

## Architecture

- **`config/schema.py`** — Pydantic model (`AppConfig`) defining the configuration shape.
- **`config/local.py`** — `LocalConfigLoader` reads config from a local JSON file.
- **`config/manager.py`** — `ConfigManager` chains multiple loaders and returns the first successful result.

## Usage

```python
from config.local import LocalConfigLoader
from config.manager import ConfigManager

manager = ConfigManager()
manager.register_loader(LocalConfigLoader("config.json"))
cfg = manager.load()
print(cfg.app_name)
```

## Adding a New Loader

Create a class with a `load() -> AppConfig` method and register it with the manager. Loaders are tried in registration order; the first one that succeeds wins.

## Running Tests

```bash
pip install pydantic pytest
pytest tests/
```
