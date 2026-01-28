# Project You: Industry Readiness Assessment Platform

A comprehensive platform designed to assess and improve industry readiness through multi-format tests, detailed reporting, and personalized journey tracking. The application combines distinct behavioral psychology models (PRI) with technical assessments to provide a holistic view of a candidate's potential.

## 🚀 Features

-   **PRI Assessment Engine**: Proprietary algorithm for calculating Purpose, Relevance, and Identity scores to determine user archetypes.
-   **Multi-Format Assessments**: Support for technical quizzes and deep behavioral analysis.
-   **AI-Driven Insights**: Automated generation of personalized reports and "Meet Yourself" reflection sessions using OpenAI/Gemini.
-   **Dynamic Reporting**: PDF report generation with granular insights and visual scoring.
-   **Personalized Journey**: A 7-day reflection journey unlocking daily based on user assessment results.
-   **Security**: Production-ready auth (JWT), HTTPS enforcement, and secure headers.
-   **High-Performance**: Sub-20ms API response times via optimized SQLAlchemy queries and composite indexing.

## 🏗 System Architecture

The project follows a modern client-server architecture:

```mermaid
graph TD
    Client[React Frontend] -->|REST API| LB[Load Balancer/Nginx]
    LB -->|HTTPS| API[FastAPI Backend]
    
    subgraph Backend Services
        API --> Auth[Auth Service]
        API --> Tests[Test Engine]
        API --> Submissions[Submission Processor]
        
        Submissions -->|Async Task| Background[Background Workers]
        Background -->|Generate| AI[AI Service (OpenAI/Gemini)]
        Background -->|Calculate| PRI[PRI Engine]
    end
    
    subgraph Data Layer
        API --> DB[(PostgreSQL)]
        API --> Redis[(Redis Cache)]
    end
```

## 🔄 Data & User Flows

### 1. Authentication Flow
1.  **Signup/Login**: User credentials are validated.
2.  **Token Generation**: valid `access_token` (JWT) is returned.
3.  **Session**: Frontend attaches this token to `Authorization` header for all protected requests.

### 2. Assessment Flow
1.  **Selection**: User fetches available tests (`GET /tests`).
2.  **Engagement**: User answers questions. Questions map to specific PRI dimensions via weighted options.
    *   *Option 1-4*: Standard weights.
    *   *Option 5*: Weighted for Purpose (P), Relevance (R), Identity (I).
3.  **Submission**: User submits answers (`POST /submissions`).
    *   Server validates question integrity.
    *   **Synchronous**: Raw scores are calculated immediately.
    *   **Asynchronous**: A background task is triggered for report generation.

### 3. PRI Engine & Report Generation (Background)
1.  **Normalization**: Raw weights are normalized against age and demographic factors.
2.  **Classification**: The `ArchetypeClassifier` determines the user's "Final Archetype" (e.g., "Explorer", "Builder").
3.  **AI Analysis**:
    *   **Input**: User profile + Signals (Tags) + Scores.
    *   **Processing**: LLM generates a cohesive narrative ("Your Core Story", "Hidden Strengths").
4.  **Completion**: PDF is generated, and the submission status updates to `completed`.

## 🛠 Tech Stack

### Backend
-   **Core**: Python 3.10+, FastAPI
-   **Database**: PostgreSQL, SQLAlchemy (ORM)
-   **Async Tasks**: Python `asyncio` + BackgroundTasks
-   **AI**: OpenAI API / Google Gemini
-   **Monitoring**: Sentry
-   **Caching**: Redis (Rate Limiting)

### Frontend
-   **Core**: React 19, Vite
-   **Styling**: TailwindCSS v4
-   **State**: Zustand
-   **Network**: Axios

## 📂 Project Structure

```text
project-you/
├── backend/
│   ├── core/           # Config (Env), Security (JWT), Database
│   ├── models.py       # SQLAlchemy Tables (Users, Submissions, Questions)
│   ├── routers/        # API Endpoints
│   │   ├── auth.py         # Login/Signup
│   │   ├── tests.py        # Test Listing (Optimized)
│   │   ├── submissions.py  # Scoring Logic
│   │   └── journey.py      # Reflection Journey
│   ├── services/       # Business Logic
│   │   └── pri/            # PRI Calculation & AI Prompts
│   └── templates/      # HTML Templates for PDF Reports
└── frontend/           # React Application
```

## 🏁 Getting Started

### Prerequisites
-   Python 3.10+
-   Node.js 16+
-   PostgreSQL

### Backend Setup
1.  Navigate to `backend`:
    ```bash
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
2.  Configure `.env` (Use `.env.example` as a template).
3.  Run Server:
    ```bash
    uvicorn main:app --reload
    ```
    *API is available at `http://localhost:8000`*

### Frontend Setup
1.  Navigate to `frontend`:
    ```bash
    cd frontend
    npm install
    ```
2.  Run Dev Server:
    ```bash
    npm run dev
    ```
    *App is available at `http://localhost:5173`*

## 🔒 Security & Performance
-   **Composite Indexing**: Optimized `(user_id, test_id, created_at)` index for instant submission lookups.
-   **N+1 Query Elimination**: Test listing endpoint uses SQL joins to prevent thousands of unnecessary queries.
-   **Rate Limiting**: `slowapi` protects auth and submission endpoints from abuse.
