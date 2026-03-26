# GenAI SRS Backend – Mongo Auth Phase

FastAPI backend that exposes `/auth/signup`, `/auth/login`, and `/auth/me` using MongoDB (Motor) for persistence, bcrypt for password hashing, and JWT access tokens.

## 1. Prerequisites

- Python 3.11+ (project uses 3.13 in dev)
- MongoDB running locally (default URI `mongodb://localhost:27017`)
- Optional: SQLite file `srs_app.db` if you plan to migrate legacy users

## 2. Environment Variables

Create `.env` in the project root (or copy from `.env.example`) with:

```
MONGODB_URL=mongodb://localhost:27017
DB_NAME=genai_srs
SECRET_KEY=replace-with-a-long-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

You can also set `SQLITE_URL=sqlite:///./srs_app.db` if you plan to run the migration script.

## 3. Install & Run

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` to exercise the API.

## 4. Tests

The suite uses `pytest` + `httpx.AsyncClient`. Tests target a dedicated Mongo database called `test_genai_srs`.

```powershell
pytest -q
```

Ensure MongoDB is running locally before executing tests.

## 5. Migration (SQLite → MongoDB)

If you have existing users in `srs_app.db`, run:

```powershell
python migration\migrate_sql_to_mongo.py
```

The script reflects the legacy `users` table with SQLAlchemy, copies the rows, and inserts them into Mongo while preserving hashed passwords. Duplicate emails are ignored thanks to Mongo’s unique index on `users.email`.

## 6. API Summary

| Endpoint         | Method | Description                           |
|------------------|--------|---------------------------------------|
| `/auth/signup`   | POST   | Register with `{email, password, full_name?}` |
| `/auth/login`    | POST   | Obtain JWT via `{email, password}`    |
| `/auth/me`       | GET    | Return the authenticated user profile |
| `/health`        | GET    | MongoDB connectivity check            |

Authorization: copy the `access_token` from `/auth/login` and send `Authorization: Bearer <token>` when calling `/auth/me`.


