# AI-Powered PR Review Agent (Free LLM Version)

Production-ready MVP with a **separate FastAPI backend** and **React + Vite + Tailwind frontend**.

- Auth with JWT + bcrypt password hashing
- Protected PR review workflow
- GitHub PR diff fetch + AI analysis using **Ollama (free local LLM)**
- Structured issue output with severity levels
- Review history dashboard
- SQLite local fallback, PostgreSQL-ready
- Rate limiting middleware with stricter `/review` limit

## Folder Structure

```text
.
├── backend
│   ├── .env.example
│   ├── requirements.txt
│   └── app
│       ├── __init__.py
│       ├── main.py
│       ├── api
│       │   ├── __init__.py
│       │   ├── deps.py
│       │   └── routes
│       │       ├── __init__.py
│       │       ├── auth.py
│       │       └── review.py
│       ├── core
│       │   ├── __init__.py
│       │   ├── config.py
│       │   ├── database.py
│       │   ├── rate_limit.py
│       │   └── security.py
│       ├── models
│       │   ├── __init__.py
│       │   ├── review.py
│       │   └── user.py
│       ├── schemas
│       │   ├── __init__.py
│       │   ├── auth.py
│       │   └── review.py
│       └── services
│           ├── __init__.py
│           ├── github_service.py
│           ├── llm_service.py
│           └── review_service.py
├── frontend
│   ├── .env.example
│   ├── index.html
│   ├── package.json
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   ├── vite.config.js
│   └── src
│       ├── App.jsx
│       ├── index.css
│       ├── main.jsx
│       ├── api
│       │   └── axios.js
│       ├── components
│       │   ├── Badge.jsx
│       │   ├── Button.jsx
│       │   ├── Card.jsx
│       │   ├── EmptyState.jsx
│       │   ├── Input.jsx
│       │   ├── IssueCard.jsx
│       │   ├── Navbar.jsx
│       │   ├── ProtectedRoute.jsx
│       │   ├── SkeletonLoader.jsx
│       │   └── Spinner.jsx
│       ├── context
│       │   └── AuthContext.jsx
│       └── pages
│           ├── DashboardPage.jsx
│           ├── LoginPage.jsx
│           ├── ReviewPage.jsx
│           └── SignupPage.jsx
└── README.md
```

## Backend Setup (FastAPI)

### 1) Create virtual environment and install dependencies

```bash
cd backend
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS/Linux
# source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Configure environment

```bash
cp .env.example .env
```

Update at least:

- `JWT_SECRET_KEY` with a strong value
- `DATABASE_URL` (optional PostgreSQL)
- `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` (for website-based GitHub connect)

GitHub OAuth App setup:

1. GitHub Settings -> Developer settings -> OAuth Apps -> New OAuth App
2. Authorization callback URL: `http://localhost:8000/github/callback`
3. Copy Client ID and Client Secret into `backend/.env`

PostgreSQL example:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/prism_ai
```

### 3) Run API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend base URL: `http://localhost:8000`

## Ollama Setup (Free LLM)

Install Ollama from: https://ollama.com/download

```bash
ollama pull llama3
ollama serve
```

Backend expects Ollama at `http://localhost:11434` by default.

## Frontend Setup (React + Vite + Tailwind)

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Frontend URL: `http://localhost:5173`

Note: In local dev, frontend uses a Vite proxy by default (`/api -> http://localhost:8000`) so CORS issues are minimized even if Vite runs on a different localhost port.

## Environment Files

### `backend/.env.example`

```env
APP_NAME=AI PR Review Agent API
ENVIRONMENT=development
DATABASE_URL=sqlite:///./app.db
JWT_SECRET_KEY=replace-with-a-strong-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
CORS_ALLOW_ORIGIN_REGEX=https?://(localhost|127\.0\.0\.1)(:\d+)?$

GITHUB_API_BASE_URL=https://api.github.com
GITHUB_OAUTH_AUTHORIZE_URL=https://github.com/login/oauth/authorize
GITHUB_OAUTH_TOKEN_URL=https://github.com/login/oauth/access_token
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
GITHUB_OAUTH_REDIRECT_URI=http://localhost:8000/github/callback
FRONTEND_URL=http://localhost:5173
TOKEN_ENCRYPTION_KEY=

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
LLM_MAX_RETRIES=3
LLM_TIMEOUT_SECONDS=90
MAX_DIFF_CHARS=18000

GENERAL_RATE_LIMIT_PER_MIN=120
REVIEW_RATE_LIMIT_PER_MIN=20
```

### `frontend/.env.example`

```env
VITE_API_URL=
VITE_PROXY_TARGET=http://localhost:8000
```

## API Endpoints

### Auth

- `POST /auth/signup`
- `POST /auth/login`
- `GET /auth/me` (protected)
- `GET /auth/github/login-url`

### Reviews

- `POST /review` (protected)
- `GET /reviews` (protected)

### GitHub OAuth

- `GET /github/connect-url` (protected)
- `GET /github/status` (protected)
- `GET /github/repos-pending-prs` (protected)
- `POST /github/disconnect` (protected)
- `GET /github/callback` (GitHub redirect target for both connect + GitHub sign-in)

## Example cURL Tests

### Signup

```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"StrongPass123"}'
```

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"StrongPass123"}'
```

Copy `access_token` from login response.

### Get Current User

```bash
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Submit PR Review (uses connected GitHub token if available)

```bash
curl -X POST http://localhost:8000/review \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "repo_owner":"octocat",
    "repo_name":"Hello-World",
    "pr_number":1347
  }'
```

### List Past Reviews

```bash
curl http://localhost:8000/reviews \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Deployment

## Deploy Backend on Render

1. Create a new **Web Service** and point to repo root.
2. Set Root Directory: `backend`
3. Build Command:

```bash
pip install -r requirements.txt
```

4. Start Command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

5. Add environment variables from `backend/.env.example`.
6. Use Render PostgreSQL and set `DATABASE_URL` accordingly.
7. Set `CORS_ORIGINS` to your Vercel frontend URL.

## Deploy Frontend on Vercel

1. Import project in Vercel.
2. Set Root Directory: `frontend`
3. Build Command: `npm run build`
4. Output Directory: `dist`
5. Set env var:

```env
VITE_API_URL=https://your-render-backend.onrender.com
```

## Security Notes

- Passwords are hashed with bcrypt.
- JWT tokens expire (`ACCESS_TOKEN_EXPIRE_MINUTES`).
- GitHub token is validated before PR fetch.
- Connected GitHub OAuth token is stored encrypted server-side.
- Rate limiting is applied globally and specifically to `/review`.
- No secrets are hardcoded in frontend or backend code.

## Verified Locally

- `python -m compileall backend/app` passed.
- `npm run build` passed.
