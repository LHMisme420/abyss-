from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import random

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

agents = [
    "Math/Physics Researcher",
    "Critic & Debater", 
    "Code Writer",
    "Evolutor"
]

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.get_template("index.html").render({"request": request})

@app.post("/run")
async def run_swarm(request: Request):
    body = await request.json()
    seed = body.get("prompt", "Find something new about primes")
    history = f"User seed: {seed}\n\n"
    current_agents = agents.copy()

    for round in range(6):
        for name in current_agents:
            # In v1 this will call real LLM — for now we fake it so it runs instantly
            fake_responses = [
                f"I found that
