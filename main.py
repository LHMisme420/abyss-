from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json

app = FastAPI()

# Serve your index.html (the one you're seeing)
@app.get("/")
async def home():
    return HTMLResponse(open("index.html", "r", encoding="utf-8").read())

# This is the endpoint your frontend is calling
@app.post("/run")
async def run(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "").strip()

    if not prompt:
        return JSONResponse({"error": "No prompt provided"}, status_code=400)

    # ←←←←← YOUR ACTUAL LOGIC GOES HERE ←←←←←
    # For now, just echo + add a funny response
    fake_response = f"""
[SWARM ACTIVATED]

Seed prompt received:
"{prompt}"

All agents are now awake and extremely enthusiastic.
They are arguing about who gets to respond first.
...consensus achieved.

Answer: The swarm thinks this is a great prompt and you should feel proud.
    """.strip()

    # The frontend expects { "history": [ ...messages ] }
    # Adjust the format to whatever your JS expects
    return JSONResponse({
        "history": [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": fake_response}
        ]
    })
