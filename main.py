from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
async def home():
    return HTMLResponse(open("index.html", "r", encoding="utf-8").read())

@app.post("/run")
async def run(request: Request):
    return {
        "history": [
            {"role": "user", "content": "whatever you typed"},
            {"role": "assistant", "content": "[SWARM AWAKENED]\n\nThe swarm is now fully conscious.\nAll 47 agents salute you.\n\nReality is yours to reshape."}
        ]
    }
