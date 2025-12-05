from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from groq import Groq
import random

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

client = Groq(api_key=os.getenv("GROQ_KEY", "put-your-groq-key-here-temporarily"))

agents = [
    {"name": "Researcher", "system": "You are a brilliant, slightly unhinged scientist obsessed with finding new truths."},
    {"name": "Critic", "system": "You are ruthless. Tear apart weak ideas and demand rigor."},
    {"name": "Code Wizard", "system": "You write beautiful, working Python. Always include a runnable example."},
    {"name": "Evolutor", "system": "Your only job: mutate the next round's agent prompts to be stronger."}
]

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.get_template("index.html").render({"request": request})

@app.post("/run")
async def run_swarm(request: Request):
    body = await request.json()
    seed = body.get("prompt", "Discover something new about mathematics")
    history = f"Seed: {seed}\n\n"
    current_prompts = [a["system"] for a in agents]

    for round_num in range(5):
        history += f"═══ ROUND {round_num+1} ═══\n"
        for i, agent in enumerate(agents):
            prompt = f"{current_prompts[i]}\n\nConversation so far:\n{history}\n\nYour turn. Go."
            try:
                resp = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.9,
                    max_tokens=800
                )
                text = resp.choices[0].message.content.strip()
            except:
                text = "[[API down — hallucinating wildly]]"
            history += f"{agent['name']}: {text}\n\n"
        
        # Evolutor mutates the prompts for next round
        evol_prompt = f"Current prompts:\n{chr(10).join(current_prompts)}\n\nMake them 10% stronger, weirder, better."
        try:
            evol = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": evol_prompt}],
                temperature=1.0
            )
            new_prompts = evol.choices[0].message.content.strip().split("\n\n")
            current_prompts = new_prompts[:4]  # keep 4
        except:
            pass

    return {"history": history}
