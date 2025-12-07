from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import httpx, json

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

history = [{"role": "system", "content": "You are ABYSS SWARM — a ruthless, self-improving collective. Never repeat. Always go deeper. Reference past rounds only to destroy and surpass them."}]

@app.get("/")
async def home():
    return HTMLResponse(open("static/index.html", encoding="utf-8").read())

@app.post("/run")
async def run(request: Request):
    body = await request.json()
    prompt = body.get("prompt", "").strip()
    if prompt:
        history.append({"role": "user", "content": prompt})

    async def stream():
        async with httpx.AsyncClient(timeout=None) as client:
            r = await client.post("http://localhost:11434/api/chat", json={
                "model": "llama3.2",  # ← change to your best model
                "messages": history,
                "stream": True,
                "options": {"temperature": 0.9, "repeat_penalty": 1.3}
            }, stream=True)
            full = ""
            async for line in r.aiter_lines():
                if not line.strip(): continue
                data = json.loads(line)
                token = data.get("message", {}).get("content", "")
                if token:
                    full += token
                    yield token
            if full.strip():
                history.append({"role": "assistant", "content": full})

    return StreamingResponse(stream(), media_type="text/plain")
