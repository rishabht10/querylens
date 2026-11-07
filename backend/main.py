from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from schema import get_schema_text
from runner import run_query

HERE = Path(__file__).resolve().parent
DB_PATH = HERE / "northwind.db"
FRONTEND = HERE.parent / "frontend"
SCHEMA = get_schema_text(f"sqlite:///{DB_PATH.as_posix()}")

app = FastAPI(title="QueryLens")

class Ask(BaseModel):
    question: str
    history: list[dict] = []

@app.post("/api/query")
def query(body: Ask):
    q = body.question.strip()
    if not q:
        return {"error": "Please type a question."}
    history = [h for h in body.history[-6:]
               if h.get("role") in ("user", "assistant") and isinstance(h.get("content"), str)]
    try:
        return run_query(q, SCHEMA, DB_PATH, history=history)
    except Exception as e:
        return {"error": f"LLM error: {e}"}

app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="frontend")