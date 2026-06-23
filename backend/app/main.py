import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

APP_DIR = os.path.dirname(os.path.abspath(__file__))
AGENT_PATH = os.path.join(APP_DIR, "agent")
TOOLS_PATH = os.path.join(APP_DIR, "tools")

for path in [AGENT_PATH, TOOLS_PATH]:
    if path not in sys.path:
        sys.path.insert(0, path)

from claude_client import ask_agent_with_data

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Question(BaseModel):
    text: str


@app.post("/ask")
def ask(question: Question):
    result = ask_agent_with_data(question.text)
    return result


@app.get("/")
def root():
    return {"status": "API en ligne"}
