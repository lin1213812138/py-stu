### Task 2: Create .env.development / .env.test / .env.staging / .env.production

**Files:**
- Create: `.env.development` (copy from existing `.env`)
- Create: `.env.test`
- Create: `.env.staging`
- Create: `.env.production`

- [ ] **Step 1: Create .env.development** (copy from `.env`)
  Copy-Item -LiteralPath ".env" -Destination ".env.development"

- [ ] **Step 2: Create .env.test**
  Content:
  APP_NAME=python-stu
  ENV=test
  MONGODB_URL=mongodb://localhost:27017
  MONGODB_DATABASE=app_test
  REDIS_URL=redis://localhost:6379
  JWT_SECRET=test-secret-key
  JWT_ACCESS_EXPIRE=1800
  JWT_REFRESH_EXPIRE=604800
  CORS_ORIGINS=["*"]

- [ ] **Step 3: Create .env.staging**
  Content:
  APP_NAME=python-stu
  ENV=staging
  MONGODB_URL=mongodb://staging-mongo:27017
  MONGODB_DATABASE=app
  REDIS_URL=redis://staging-redis:6379
  JWT_SECRET=staging-secret-key
  JWT_ACCESS_EXPIRE=1800
  JWT_REFRESH_EXPIRE=604800
  CORS_ORIGINS=["https://staging.example.com"]

- [ ] **Step 4: Create .env.production**
  Content:
  APP_NAME=python-stu
  ENV=production
  MONGODB_URL=mongodb://prod-mongo:27017
  MONGODB_DATABASE=app
  REDIS_URL=redis://prod-redis:6379
  JWT_SECRET=prod-secret-key
  JWT_ACCESS_EXPIRE=1800
  JWT_REFRESH_EXPIRE=604800
  CORS_ORIGINS=["https://example.com"]

- [ ] **Step 5: Verify Settings can load each env file**
  Commands:
  $env:ENV="development"; .venv\Scripts\python -c "from app.core.config import Settings; print(Settings().ENV, Settings().MONGODB_URL)"
  $env:ENV="test"; .venv\Scripts\python -c "from app.core.config import Settings; print(Settings().ENV, Settings().MONGODB_URL)"
  $env:ENV="staging"; .venv\Scripts\python -c "from app.core.config import Settings; print(Settings().ENV, Settings().MONGODB_URL)"
  $env:ENV="production"; .venv\Scripts\python -c "from app.core.config import Settings; print(Settings().ENV, Settings().MONGODB_URL)"
  
  Expected: each env shows different MONGODB_URL

- [ ] **Step 6: Commit**
  git add .env.development .env.test .env.staging .env.production
  git commit -m "feat: add environment-specific .env files"
