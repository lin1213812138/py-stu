# Task 1 Report: Dynamic env_file Loading

## What I Implemented
- Modified `app/core/config.py` to dynamically load `.env.{ENV}` based on the `ENV` system environment variable
- Created `tests/test_config.py` with 3 test cases covering instantiation, fallback, and override

## Test Results
- **Baseline (before changes):** 3/3 passed
- **After changes:** 3/3 passed
- **Full suite (after changes):** 6/10 passed (4 pre-existing failures in `test_auth.py` and `test_user.py` — `AttributeError: username` — unrelated to config)
- **TDD Evidence:** GREEN/GREEN — tests passed before and after implementation

## Files Changed
| File | Action |
|------|--------|
| `app/core/config.py` | Modified — replaced static `model_config` with dynamic `__init__` that selects `.env.{ENV}` file |
| `tests/test_config.py` | Created |

## Self-Review Findings
- The `SettingsConfigDict` import is used for the `model_config` field typing, which is the modern pydantic-settings approach
- The `Path` import is specifically used for file existence check before falling back to `.env`
- Default `ENV` is `"development"` and falls back to `.env` if `.env.development` doesn't exist

## Issues or Concerns
- 4 pre-existing test failures in `test_auth.py` and `test_user.py` (`AttributeError: username`) — unrelated to this task

## Fix: Missing test for env file loading & log warning (2026-07-01)

### What got fixed
- Added `test_env_file_is_loaded_when_exists` to verify `.env.{ENV}` file contents are reflected when the file exists
- Added `logger.warning` in `Settings.__init__` when neither `.env.{ENV}` nor `.env` is found, avoiding silent fallback to defaults

### Test results
- `tests/test_config.py` — **4/4 passed** (new test included)
- Full suite — **7/11 passed** (same 4 pre-existing failures in auth/user)

### Commit
- `6cd9e4f` — `fix: add env file loading test and fallback warning`
