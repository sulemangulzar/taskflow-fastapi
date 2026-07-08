# TaskFlow deployment checklist

This repository now has:

- FastAPI backend in this folder.
- Basic React/Vite frontend in `frontend/`.
- Render Blueprint example in `render.yaml`.
- Vercel frontend config in `frontend/vercel.json`.

## Local development

### Backend

```bash
cp .env.example .env
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
```

Backend URL: `http://localhost:8000`

API docs:

- Swagger: `http://localhost:8000/docs`
- Scalar: `http://localhost:8000/scalar`
- Health: `http://localhost:8000/health`

### Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Frontend URL: `http://localhost:5173`

## Deploy backend on Render

### Option A: Blueprint

1. Push this repo to GitHub.
2. In Render, choose **New > Blueprint**.
3. Select the repo and use `render.yaml`.
4. Fill the secret mail variables when Render asks:
   - `MAIL_USERNAME`
   - `MAIL_PASSWORD`
   - `MAIL_FROM`
   - `MAIL_SERVER`
   - `MAIL_PORT`
5. After the service is created, replace the placeholder `DOMAIN` value with your real Render backend URL, for example `https://your-service.onrender.com`.
6. After your Vercel frontend is deployed, set `FRONTEND_ORIGINS` to your exact frontend URL, for example `https://your-app.vercel.app`.

### Option B: Manual Render web service

Use these settings:

- Runtime: Python
- Root directory: this backend folder, if your repo has a parent folder
- Build command: `pip install -r requirements.txt && alembic upgrade head`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Health check path: `/health`

Create attached Render PostgreSQL and Redis services, then set these backend env vars:

```text
DATABASE_URL=postgresql+asyncpg://...
REDIS_URL=redis://...
REDIS_HOST=...
REDIS_PORT=...
DEBUG=false
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
JWT_SECRET_KEY=<long-random-secret>
JWT_ALGORITHM=HS256
JWT_ISSUER=taskflow-api
JWT_AUDIENCE=taskflow-client
DOMAIN=https://your-api.onrender.com
FRONTEND_ORIGINS=https://your-frontend.vercel.app
CORS_ORIGIN_REGEX=https://.*\.vercel\.app
ALLOWED_HOSTS=localhost,127.0.0.1,*.onrender.com
MAIL_USERNAME=...
MAIL_PASSWORD=...
MAIL_FROM=...
MAIL_SERVER=...
MAIL_PORT=2525
```

Render's PostgreSQL URL may start with `postgres://` or `postgresql://`. The app automatically normalizes those to `postgresql+asyncpg://` at startup for SQLAlchemy's async engine.

## Deploy frontend on Vercel

1. Import the same GitHub repo into Vercel.
2. Set the Vercel **Root Directory** to `frontend`.
3. Build command: `npm run build`.
4. Output directory: `dist`.
5. Add environment variable:

```text
VITE_API_URL=https://your-api.onrender.com
```

6. Deploy.
7. Copy the Vercel production URL and update Render backend env var `FRONTEND_ORIGINS` to that exact URL.
8. Redeploy/restart the Render service after changing env vars.

## Things checked/fixed for deployment

- `TrustedHostMiddleware` is now configurable using `ALLOWED_HOSTS`, so Render hostnames are not blocked.
- CORS is now configurable using `FRONTEND_ORIGINS` and `CORS_ORIGIN_REGEX`, so Vercel can call the API.
- `requirements.txt` now includes packages used by the app such as Redis, Celery, SlowAPI, and FastAPI-Mail.
- Frontend uses `VITE_API_URL`, so local and production API URLs can differ.
- React frontend stores the bearer token in local storage and sends it as `Authorization: Bearer <token>`.

## Notes

- The frontend is intentionally simple. It supports signup, login, project create/list/delete, task create/list/status update/delete, and token refresh.
- Signup sends an email verification link when mail/Celery are configured, but the basic frontend can login immediately after signup.
- For production, consider using a paid Render instance because free services can sleep and make the first API call slow.
