from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import random

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

fallback_responses = [
    "Discovered: There are 25 primes under 100—next one's 101!",
    "Critique: That's basic. Push to twin primes for novelty.",
    "Code: def sieve(n): return [i for i in range(2, n) if all(i % j != 0 for j in range(2, int(i**0.5)+1))]",
    "Evolving: Next round, add quantum-inspired randomness."
]

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/run")
async def run_swarm(request: Request):
    body = await request.json()
    seed = body.get("prompt", "Find truth")
    history = f"Seed: {seed}\n\n"
    agents = ["Researcher", "Critic", "Code Wizard", "Evolutor"]

    for r in range(6):
        history += f"═══ ROUND {r+1} ═══\n"
        for agent in agents:
            text = random.choice(fallback_responses)
            history += f"{agent}: {text}\n\n"
        if random.random() > 0.5:
            agents[-1] = "Quantum Evolutor"

    return {"history": history}
