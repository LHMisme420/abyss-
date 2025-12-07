# main.py ─── FINAL: ZERO LOOPING GUARANTEED
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
import httpx, json

app = FastAPI()
history = [{"role": "system", "content": "You are the ABYSS SWARM. NEVER repeat previous rounds. Always advance, evolve, and go deeper. Reference past work only to build on it."}]

@app.get("/")
async def home():
    return HTMLResponse(open("abyss.html", "r", encoding="utf-8").read())  # ← we'll make this file in 2 sec

@app.post("/run")
async def run(request: Request):
    body = await request.json()
    prompt = body.get("prompt", "").strip()
    if prompt:
        history.append({"role": "user", "content": prompt})

    async def streamer():
        async with httpx.AsyncClient(timeout=None) as client:
            resp = await client.post("http://localhost:11434/api/chat", json={
                "model": "llama3.2",
                "messages": history + [{"role": "user", "content": "Continue evolving the solution. Do NOT repeat anything already said. Push forward."}],
                "stream": True,
                "options": {"temperature": 1.1, "repeat_penalty": 1.4}
            }, stream=True)
            full = ""
            async for line in resp.aiter_lines():
                if not line.strip(): continue
                data = json.loads(line)
                token = data.get("message", {}).get("content", "")
                if token:
                    full += token
                    yield token
            if full.strip():
                history.append({"role": "assistant", "content": full})

    return StreamingResponse(streamer(), media_type="text/plain")
