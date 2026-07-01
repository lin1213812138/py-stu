
**鏂囦欢锛?*
- 淇敼锛歚app/core/config.py`
- 鍒涘缓锛歚tests/test_config.py`

**鎺ュ彛锛?*
- 娑堣垂锛氱幇鏈?`Settings` 绫荤殑娑堣垂鑰咃紙`from app.core.config import settings`锛夆€斺€旀帴鍙ｄ笉鍙?- 浜у嚭锛歚Settings` 绫绘瀯閫犳椂鏍规嵁 `os.getenv("ENV", "development")` 鍔犺浇 `.env.{ENV}`锛屼笉瀛樺湪鍒欓檷绾у埌 `.env`

- [ ] **Step 1锛氬垱寤烘祴璇曟枃浠?*

```python
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
```

- [ ] **Step 2锛氳繍琛屾祴璇曪紝纭娴嬭瘯妗嗘灦姝ｅ父**

```bash
.venv\Scripts\python -m pytest tests/test_config.py -v
```

棰勬湡锛? passed锛堟棫浠ｇ爜宸茶兘姝ｅ父瀹炰緥鍖?Settings锛?
- [ ] **Step 3锛氫慨鏀?config.py 瀹炵幇鍔ㄦ€佸姞杞?*

```python
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENV: str = "development"
    APP_NAME: str = "python-stu"
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "app"
    REDIS_URL: str = "redis://localhost:6379"
    JWT_SECRET: str = "change-this-in-production"
    JWT_ACCESS_EXPIRE: int = 1800
    JWT_REFRESH_EXPIRE: int = 604800
    CORS_ORIGINS: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
    )

    def __init__(self, **kwargs):
        env = os.getenv("ENV", "development")
        env_file = f".env.{env}"
        if not Path(env_file).exists():
            env_file = ".env"
        super().__init__(_env_file=env_file, **kwargs)


settings = Settings()
```

- [ ] **Step 4锛氳繍琛屾祴璇曪紝楠岃瘉閫氳繃**

```bash
.venv\Scripts\python -m pytest tests/test_config.py -v
```

棰勬湡锛? passed

- [ ] **Step 5锛氭彁浜?*

```bash
git add app/core/config.py tests/test_config.py
git commit -m "feat: dynamic env_file loading based on ENV system variable"
```

---

### Task 2锛氬垱寤?.env.development / .env.test / .env.staging / .env.production

**鏂囦欢锛?*
- 鍒涘缓锛歚.env.development`锛堜粠鐜版湁 `.env` 澶嶅埗锛?- 鍒涘缓锛歚.env.test`
- 鍒涘缓锛歚.env.staging`
- 鍒涘缓锛歚.env.production`

- [ ] **Step 1锛氬垱寤?.env.development**锛堜粠 `.env` 澶嶅埗锛?
```bash
Copy-Item -LiteralPath ".env" -Destination ".env.development"
```

- [ ] **Step 2锛氬垱寤?.env.test**

鍐呭锛?```
APP_NAME=python-stu
ENV=test

MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=app_test

REDIS_URL=redis://localhost:6379

JWT_SECRET=test-secret-key
JWT_ACCESS_EXPIRE=1800
JWT_REFRESH_EXPIRE=604800

CORS_ORIGINS=["*"]
```

- [ ] **Step 3锛氬垱寤?.env.staging**

鍐呭锛?```
APP_NAME=python-stu
ENV=staging

MONGODB_URL=mongodb://staging-mongo:27017
MONGODB_DATABASE=app

REDIS_URL=redis://staging-redis:6379

JWT_SECRET=staging-secret-key
JWT_ACCESS_EXPIRE=1800
JWT_REFRESH_EXPIRE=604800

CORS_ORIGINS=["https://staging.example.com"]
```

- [ ] **Step 4锛氬垱寤?.env.production**

鍐呭锛?```
APP_NAME=python-stu
ENV=production

MONGODB_URL=mongodb://prod-mongo:27017
MONGODB_DATABASE=app

REDIS_URL=redis://prod-redis:6379

JWT_SECRET=prod-secret-key
JWT_ACCESS_EXPIRE=1800
JWT_REFRESH_EXPIRE=604800

CORS_ORIGINS=["https://example.com"]
```

- [ ] **Step 5锛氶獙璇?Settings 鑳藉姞杞藉悇鐜鏂囦欢**

```bash
$env:ENV="development"; .venv\Scripts\python -c "from app.core.config import Settings; print(Settings().ENV, Settings().MONGODB_URL)"
$env:ENV="test"; .venv\Scripts\python -c "from app.core.config import Settings; print(Settings().ENV, Settings().MONGODB_URL)"
$env:ENV="staging"; .venv\Scripts\python -c "from app.core.config import Settings; print(Settings().ENV, Settings().MONGODB_URL)"
$env:ENV="production"; .venv\Scripts\python -c "from app.core.config import Settings; print(Settings().ENV, Settings().MONGODB_URL)"
```

棰勬湡锛氭瘡涓幆澧冭緭鍑轰笉鍚岀殑 `MONGODB_URL`
- development 鈫?`localhost`
- test 鈫?`localhost`锛坉atabase 涓?`app_test`锛?- staging 鈫?`staging-mongo:27017`
- production 鈫?`prod-mongo:27017`

- [ ] **Step 6锛氭彁浜?*

```bash
git add .env.development .env.test .env.staging .env.production
git commit -m "feat: add environment-specific .env files"
```

---

### Task 3锛氬垱寤?.dockerignore

**鏂囦欢锛?*
- 鍒涘缓锛歚.dockerignore`

- [ ] **Step 1锛氬垱寤?.dockerignore**

```
.venv/
