# Tokeep Backend

This project is a FastAPI backend for managing chat sessions with a mock LLM (Large Language Model) interface.

## Features

- Create, list, and delete chat sessions
- Send chat prompts and receive mock responses
- Track token usage and cost per session
- Usage summary endpoint

## Endpoints

- `GET /` — Health check
- `POST /sessions` — Create a new session
- `POST /chat` — Send a prompt to a session
- `GET /sessions` — List all sessions
- `GET /sessions/{session_id}` — Get session details
- `GET /usage` — Get usage summary
- `DELETE /sessions/{session_id}` — Delete a session

## Requirements

- Python 3.7+
- fastapi
- pydantic
- uvicorn

## Running

```bash
pip install fastapi uvicorn pydantic
uvicorn main:app --reload
```

---

Let me know if you want to include more details or usage examples!
