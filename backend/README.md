# GrowthOS Backend API

GrowthOS Backend is built with **FastAPI**, **Motor (MongoDB)**, **LangGraph**, **Mem0**, **Groq (llama-3.3-70b-versatile)**, and **Scikit-Learn ML Inference**.

## Architecture Overview

- **`app/main.py`**: Entry point for FastAPI application.
- **`app/api/`**: Modular REST API controllers (`auth`, `onboarding`, `dashboard`, `planner`, `reflection`, `recommendation`, `opportunity`, `notification`, `health`).
- **`app/agents/`**: Autonomous AI agents (`supervisor`, `user_understanding`, `planner`, `learning_curator`, `opportunity`, `reflection`, `notification`).
- **`app/graph/`**: Multi-agent orchestration with LangGraph workflow engine.
- **`app/memory/`**: Mem0 memory management engine (store, retrieve, update).
- **`app/llm/`**: Groq API wrapper, prompt templates, output parsers, and embeddings.
- **`app/ml/`**: Machine Learning inference engines (`growth_predictor`, `burnout_predictor`) with saved models.
- **`app/database/`**: Motor MongoDB async driver integration & collection repositories.
- **`app/services/`**: Business logic services decoupling APIs from persistence & agent workflows.
- **`app/schemas/`**: Pydantic models for request/response validation.
- **`app/middleware/`**: Auth, CORS, and HTTP logging middleware.
- **`app/config/`**: App settings, database configurations, and global constants.
- **`app/utils/`**: Security, JWT, response standardizers, and helpers.
- **`app/tests/`**: Pytest test suite for API, Auth, ML, and Agents.

## Setup & Running

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run FastAPI dev server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Swagger UI documentation will be available at `http://localhost:8000/docs`.
