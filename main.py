from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import random

app = FastAPI()
app.mount("/static", StaticFiles(directory="static", html=True), name="static")
templates = Jinja2Templates(directory="templates")

fallback_responses = [
    "I just proved that 2025 is a prime year in base-7.",
    "Your idea is garbage. Here’s why…",
    "Here’s a working sieve that’s 0.3 % faster on my laptop:",
    "Evolving… next round we add quantum tunneling to the researcher."
]

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.get_template("index.html").render({"request": request})

@app.post("/run")
async def run_swarm(request: Request):
    body = await request.json()
    seed = body.get("prompt", "Find truth")
    history = f"Seed: {seed}\n\n"

    agents = ["Researcher", " , "Critic " , "Code Wizard " , "Evolutor " ]

    for r in range(6):
        history += f"═══ ROUND {r+1} ═══\n"
        for agent in agents:
            text = random.choice(fallback_responses)
            history += f"{agent}: {text}\n\n"
        if random.random() > 0.5:
            agents[-1] = "Quantum Evolutor "

    return {"history": history}
