# Project Setup and Run Instructions

This project consists of a Python FastAPI backend and a React (Vite) frontend.

## Prerequisites

- [Python 3.8+](https://www.python.org/downloads/)
- [Node.js 16+](https://nodejs.org/)

## Backend Setup

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

4.  **Run the server:**
    
    You can use the provided restart script:
    ```bash
    ./restart_server.sh
    ```
    
    Or run uvicorn directly:
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
    
    The backend API will be available at `http://localhost:8000`.
    API Documentation (Swagger UI) is available at `http://localhost:8000/docs`.

    > **Note:** Ensure you have a `.env` file properly configured. If `templates/thinkbinary_report.html` is missing, some functionality might be limited.

## Frontend Setup

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
    
    The frontend will be available at `http://localhost:5173`.

## Running Both

You will need two terminal windows: one for the backend and one for the frontend.
