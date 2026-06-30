from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import uuid

app = FastAPI()

# temporary "database"
sessions = {}

class SessionCreate(BaseModel):
    user_id: str
    session_name: str
    provider: str = "openai"
    model: str = "gpt-4.1-mini"

@app.post("/sessions")
def create_session(session: SessionCreate):
    session_id = str(uuid.uuid4())

    sessions[session_id] = {
        "session_id": session_id,
        "user_id": session.user_id,
        "session_name": session.session_name,
        "provider": session.provider,
        "model": session.model,
        "start_time": datetime.now().isoformat(),
        "messages": [],
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_cost": 0
    }

    return sessions[session_id]