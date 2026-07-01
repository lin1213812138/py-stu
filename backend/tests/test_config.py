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
