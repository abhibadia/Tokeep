from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Session, create_engine, select
from datetime import datetime
from uuid import uuid4
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = "sqlite:///tokeep.db"
engine = create_engine(DATABASE_URL, echo=True)


class ChatSession(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str
    session_name: str
    provider: str
    model: str
    start_time: str
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_tokens: int = 0
    total_cost: float = 0


class Message(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    session_id: str
    prompt: str
    response: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost: float
    timestamp: str

class UserAPIKey(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str
    provider: str
    api_key: str
    created_at: str

class APIKeyCreate(BaseModel):
    user_id: str
    provider: str
    api_key: str


class SessionCreate(BaseModel):
    user_id: str
    session_name: str
    provider: str
    model: str


class ChatRequest(BaseModel):
    session_id: str
    prompt: str


MODEL_PRICES = {
    "gpt-4.1-mini": {
        "input": 0.0000004,
        "output": 0.0000016
    }
}


@app.on_event("startup")
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@app.get("/")
def home():
    return {"message": "Tokeep backend is running"}


@app.post("/sessions")
def create_session(session_data: SessionCreate):
    new_session = ChatSession(
        user_id=session_data.user_id,
        session_name=session_data.session_name,
        provider=session_data.provider,
        model=session_data.model,
        start_time=datetime.now().isoformat()
    )

    with Session(engine) as db:
        db.add(new_session)
        db.commit()
        db.refresh(new_session)

    return new_session

@app.post("/api-keys")
def save_api_key(key_data: APIKeyCreate):
    new_key = UserAPIKey(
        user_id=key_data.user_id,
        provider=key_data.provider,
        api_key=key_data.api_key,
        created_at=datetime.now().isoformat()
    )

    with Session(engine) as db:
        db.add(new_key)
        db.commit()
        db.refresh(new_key)

    return {
        "message": "API key saved",
        "provider": new_key.provider,
        "key_id": new_key.id
    }


@app.post("/chat")
def chat(request: ChatRequest):
    with Session(engine) as db:
        chat_session = db.get(ChatSession, request.session_id)

        statement = select(UserAPIKey).where(
            UserAPIKey.user_id == chat_session.user_id,
            UserAPIKey.provider == chat_session.provider
        )

        user_api_key = db.exec(statement).first()

        if not user_api_key:
            raise HTTPException(status_code=400, detail="No API key connected for this provider")

        user_client = OpenAI(api_key=user_api_key.api_key)

        if not chat_session:
            raise HTTPException(status_code=404, detail="Session not found")

        response = user_client.responses.create(
            model=chat_session.model,
            input=request.prompt
        )

        response_text = response.output_text

        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        total_tokens = response.usage.total_tokens

        cost = calculate_cost(
            model=chat_session.model,
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )

        message = Message(
            session_id=request.session_id,
            prompt=request.prompt,
            response=response_text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost=cost,
            timestamp=datetime.now().isoformat()
        )

        chat_session.total_input_tokens += input_tokens
        chat_session.total_output_tokens += output_tokens
        chat_session.total_tokens += total_tokens
        chat_session.total_cost += cost

        db.add(message)
        db.add(chat_session)
        db.commit()
        db.refresh(message)

        return message


@app.get("/sessions")
def get_sessions():
    with Session(engine) as db:
        statement = select(ChatSession)
        results = db.exec(statement).all()
        return results


@app.get("/sessions/{session_id}")
def get_session_details(session_id: str):
    with Session(engine) as db:
        chat_session = db.get(ChatSession, session_id)

        if not chat_session:
            raise HTTPException(status_code=404, detail="Session not found")

        statement = select(Message).where(Message.session_id == session_id)
        messages = db.exec(statement).all()

        return {
            "session": chat_session,
            "messages": messages
        }


@app.get("/usage")
def get_usage_summary():
    with Session(engine) as db:
        statement = select(ChatSession)
        sessions = db.exec(statement).all()

        return {
            "total_sessions": len(sessions),
            "total_input_tokens": sum(s.total_input_tokens for s in sessions),
            "total_output_tokens": sum(s.total_output_tokens for s in sessions),
            "total_tokens": sum(s.total_tokens for s in sessions),
            "total_cost": sum(s.total_cost for s in sessions)
        }


@app.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    with Session(engine) as db:
        chat_session = db.get(ChatSession, session_id)

        if not chat_session:
            raise HTTPException(status_code=404, detail="Session not found")

        statement = select(Message).where(Message.session_id == session_id)
        messages = db.exec(statement).all()

        for message in messages:
            db.delete(message)

        db.delete(chat_session)
        db.commit()

        return {"message": "Session deleted"}


def calculate_cost(model: str, input_tokens: int, output_tokens: int):
    if model not in MODEL_PRICES:
        return 0

    return (
        input_tokens * MODEL_PRICES[model]["input"]
        + output_tokens * MODEL_PRICES[model]["output"]
    )