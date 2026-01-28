# Project You: Industry Readiness Assessment Platform

A comprehensive platform designed to assess and improve industry readiness through multi-format tests, detailed reporting, and personalized journey tracking. The application consists of a **FastAPI** backend and a **React (Vite)** frontend.

## 🚀 Features

- **Multi-Format Assessments**: Technical and behavioral tests with various question types.
- **Detailed Reporting**: Generates PDF reports with insights using HTML templates (`templates/thinkbinary_report.html`).
- **Personalized Journey**: Track progress and readiness scores over time.
- **AI Integration**: Uses OpenAI or Gemini for advanced analysis and feedback.
- **Security**: JWT-based authentication and production-grade security practices.
- **Performance**: Redis caching and Sentry monitoring integration.

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.8+)
- **Database**: PostgreSQL (SQLAlchemy ORM)
- **Caching**: Redis
- **Validation**: Pydantic
- **Monitoring**: Sentry
- **background Tasks**: Celery (Configured in `tasks/`)

### Frontend
- **Framework**: React 19 (Vite)
- **Language**: JavaScript/JSX
- **Styling**: TailwindCSS v4
- **State Management**: Zustand
- **Icons**: Lucide React
- **Networking**: Axios

## 📋 Prerequisites

- [Python 3.8+](https://www.python.org/downloads/)
- [Node.js 16+](https://nodejs.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [Redis](https://redis.io/) (Optional for dev, recommended for features relying on caching)

## 🏁 Getting Started

### 1. Backend Setup

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Configuration:**
    Copy the example environment file and configure your secrets:
    ```bash
    cp .env.example .env
    ```
    Update `.env` with your database credentials, API keys, and JWT secret.
    *Note: `DATABASE_URL` is required.*

5.  **Run the server:**
    
    You can use the provided restart script (handles cleanup and restart):
    ```bash
    ./restart_server.sh
    ```
    
    Or run uvicorn directly:
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
    
    - API Documentation: `http://localhost:8000/docs`
    - API Root: `http://localhost:8000`

### 2. Frontend Setup

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Run the development server:**
    ```bash
    npm run dev
    ```
    
    - Frontend URL: `http://localhost:5173`

## 📂 Project Structure

```
project-you/
├── backend/
│   ├── core/           # Config, Database, Security, Monitoring
│   ├── routers/        # API Endpoints (Auth, Tests, Submissions, etc.)
│   ├── services/       # Business Logic & External Integrations
│   ├── models.py       # SQLAlchemy Database Models
│   ├── schemas.py      # Pydantic Schemas
│   ├── main.py         # Application Entry Point
│   └── ...
├── frontend/
│   ├── src/            # React Source Code
│   ├── public/         # Static Assets
│   └── ...
└── README.md
```

## 🔒 Environment Variables

Key variables in `.env`:
- `DATABASE_URL`: Connection string for PostgreSQL.
- `JWT_SECRET_KEY`: Secret for signing auth tokens.
- `OPENAI_API_KEY` / `GEMINI_API_KEY`: API keys for AI features.
- `ENVIRONMENT`: `development` or `production`.

See `backend/.env.example` for the full list.
