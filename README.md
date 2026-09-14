# Bookstore API

FastAPI + SQLModel + PostgreSQL + Alembic + JWT + Docker.

## Setup

```powershell
uv venv
.venv\Scripts\activate
uv pip install -r requirements.txt
```

## Docker

```powershell
docker compose up --build
```

Swagger: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc

## Local Alembic workflow

```powershell
alembic revision --autogenerate -m "create users authors and books"
alembic upgrade head
uvicorn app.main:app --reload
```

The project uses SQLModel as the ORM/model layer and does not call `SQLModel.metadata.create_all()`.
