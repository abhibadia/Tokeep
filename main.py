from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from uuid import uuid4

app = FastAPI()

# Temporary in-memory database
sessions = {}

# Fake pricing for now
MODEL_PRICES = {
    "gpt-4.1-mini": {
        "input": 0.0000004,
        "output": 0.0000016
    }
}


class SessionCreate(BaseModel): #struct for a mock session
    user_id: str
    session_name: str
    provider: str
    model: str


class ChatRequest(BaseModel): #struct for a mock chatrequest
    session_id: str
    prompt: str


@app.get("/") #home page (diagnose if working)
def home():
    return {"message": "Tokeep backend is running"}


@app.post("/sessions") #post sessions - this is where new sessions are added into backend thru api call
def create_session(session: SessionCreate):
    session_id = str(uuid4())

    new_session = { #new session created
        "session_id": session_id,
        "user_id": session.user_id,
        "session_name": session.session_name,
        "provider": session.provider,
        "model": session.model,
        "start_time": datetime.now().isoformat(),
        "messages": [],
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_tokens": 0,
        "total_cost": 0
    }

    sessions[session_id] = new_session #keying every unique session to hashmap - key is session id
    return new_session


@app.post("/chat")
def chat(request: ChatRequest):
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[request.session_id]

    # Fake LLM response for now
    response_text = f"Fake LLM response to: {request.prompt}"

    # Simple fake token counting
    input_tokens = len(request.prompt.split())
    output_tokens = len(response_text.split())
    total_tokens = input_tokens + output_tokens

    cost = calculate_cost(
        model=session["model"],
        input_tokens=input_tokens,
        output_tokens=output_tokens
    )

    message = {
        "prompt": request.prompt,
        "response": response_text,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "cost": cost,
        "timestamp": datetime.now().isoformat()
    }

    session["messages"].append(message)
    session["total_input_tokens"] += input_tokens
    session["total_output_tokens"] += output_tokens
    session["total_tokens"] += total_tokens
    session["total_cost"] += cost

    return message


@app.get("/sessions")
def get_sessions():
    return list(sessions.values())


@app.get("/sessions/{session_id}")
def get_session_details(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    return sessions[session_id]


@app.get("/usage")
def get_usage_summary():
    total_sessions = len(sessions)
    total_input_tokens = 0
    total_output_tokens = 0
    total_tokens = 0
    total_cost = 0

    for session in sessions.values():
        total_input_tokens += session["total_input_tokens"]
        total_output_tokens += session["total_output_tokens"]
        total_tokens += session["total_tokens"]
        total_cost += session["total_cost"]

    return {
        "total_sessions": total_sessions,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "total_tokens": total_tokens,
        "total_cost": total_cost
    }


@app.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    deleted_session = sessions.pop(session_id)

    return {
        "message": "Session deleted",
        "deleted_session": deleted_session
    }


def calculate_cost(model: str, input_tokens: int, output_tokens: int):
    if model not in MODEL_PRICES:
        return 0

    input_price = MODEL_PRICES[model]["input"]
    output_price = MODEL_PRICES[model]["output"]

    return input_tokens * input_price + output_tokens * output_price