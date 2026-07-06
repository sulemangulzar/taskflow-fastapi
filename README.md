# TaskFlow API 🚀

TaskFlow is a production-ready, highly scalable backend API for collaborative project and task management. It is built using modern Python frameworks to demonstrate advanced backend engineering concepts, including asynchronous background tasks, role-based access control (RBAC), and robust security practices.

---

## 🛠️ Tech Stack

* **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Async web framework)
* **Database:** PostgreSQL (Relational DB)
* **ORM:** [SQLModel](https://sqlmodel.tiangolo.com/) (SQLAlchemy + Pydantic)
* **Migrations:** Alembic
* **Background Tasks:** Celery + Redis
* **Authentication:** JWT (Access & Refresh Tokens) with Redis blocklisting
* **Email Service:** FastAPI-Mail (connected to Mailtrap for sandbox testing)
* **Rate Limiting:** SlowAPI (Redis-backed)

---

## ✨ Key Features

* **Advanced Authentication & Security:** 
  * Secure Signup & Login with password hashing (`passlib`/`bcrypt`).
  * JWT-based auth with short-lived access tokens and long-lived refresh tokens.
  * Secure Logout mechanism using a Redis-backed token blocklist to instantly invalidate tokens.
* **Asynchronous Email Workflows:**
  * Celery background workers process email sending without blocking the main API thread.
  * Time-limited, URL-safe token generation for **Email Verification** and **Password Resets**.
* **Complex Authorization Rules:**
  * Role-Based Access Control (Admin vs. User).
  * Project owners have full CRUD rights; assigned users can view and update their specific tasks but cannot delete them.
* **Production-Grade Protections:**
  * Global and endpoint-specific Rate Limiting via SlowAPI.
  * CORS Middleware and Trusted Host Middleware configured.
* **Automated Testing:**
  * Robust `pytest` suite utilizing an in-memory async SQLite database, mocked Redis, and bypassed Celery workers for lightning-fast unit/integration testing.

---

## 🚀 Getting Started

Follow these instructions to get a local copy up and running.

### 1. Prerequisites
* Python 3.10+
* PostgreSQL running locally or via Docker
* Redis running locally or via Docker

### 2. Installation
Clone the repository and install dependencies using `uv` (or `pip`):
```bash
git clone https://github.com/sulemangulzar/taskflow-fastapi.git
cd taskflow-fastapi/backend

# Create virtual environment and install packages
uv venv
source .venv/bin/activate
# Install your dependencies based on your setup (e.g., uv sync or uv pip install -r requirements.txt)
```

### 3. Environment Variables
Create a `.env` file in the `backend/` directory and configure the following variables:
```ini
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/taskflow_db

# Security & JWT
DEBUG=True
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
JWT_SECRET_KEY=your_super_secret_key
JWT_ALGORITHM=HS256
JWT_ISSUER=taskflow
JWT_AUDIENCE=taskflow_users
DOMAIN=localhost:8001

# Redis / Celery
REDIS_URL=redis://127.0.0.1:6379/0
REDIS_HOST=127.0.0.1
REDIS_PORT=6379

# Email Service (Mailtrap)
MAIL_USERNAME=your_mailtrap_username
MAIL_PASSWORD=your_mailtrap_password
MAIL_FROM=noreply@taskflow.com
MAIL_SERVER=sandbox.smtp.mailtrap.io
MAIL_PORT=2525
```

### 4. Database Migrations
Run Alembic to create the necessary tables in your PostgreSQL database:
```bash
alembic upgrade head
```

### 5. Running the Application

You will need two terminal windows to run both the API and the Celery background worker.

**Terminal 1: Start the Celery Worker (for background emails)**
```bash
source .venv/bin/activate
celery -A app.celery_tasks.c_app worker -E -l info
```

**Terminal 2: Start the FastAPI Server**
```bash
source .venv/bin/activate
uvicorn main:app --reload --port 8001
```

*(Optional) Start Flower to monitor Celery tasks:*
```bash
celery -A app.celery_tasks.c_app flower
```

---

## 📖 API Documentation

Once the server is running, FastAPI automatically generates interactive documentation. You can explore and test the endpoints directly from your browser:
* **Swagger UI / Scalar:** `http://localhost:8001/scalar`
* **Redoc:** `http://localhost:8001/redoc`

---

## 🧪 Running Tests

The test suite uses an in-memory async SQLite database, so it won't affect your production data. Run the tests via pytest:

```bash
export PYTHONPATH=.
pytest tests/
```