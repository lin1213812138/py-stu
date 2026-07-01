import os

import pytest

from app.core.config import Settings


@pytest.fixture(autouse=True)
def cleanup_env():
    old = os.environ.get("ENV")
    yield
    if old is None:
        os.environ.pop("ENV", None)
    else:
        os.environ["ENV"] = old


def test_settings_instantiation():
    s = Settings()
    assert isinstance(s, Settings)
    assert s.APP_NAME == "python-stu"


def test_env_fallback_to_development():
    os.environ.pop("ENV", None)
    s = Settings()
    assert s.ENV == "development"


def test_env_override_from_system():
    os.environ["ENV"] = "production"
    s = Settings()
    assert s.ENV == "production"


def test_env_file_is_loaded_when_exists(tmp_path, monkeypatch):
    env_file = tmp_path / ".env.staging"
    env_file.write_text("MONGODB_URL=mongodb://staging-mongo:27017\n")
    monkeypatch.setenv("ENV", "staging")
    monkeypatch.chdir(tmp_path)
    s = Settings()
    assert s.MONGODB_URL == "mongodb://staging-mongo:27017"
