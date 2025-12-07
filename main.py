from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import httpx          # ← new
import json           # ← new

app = FastAPI()

@app.get("/")
def home():
    return HTMLResponse("""
    <html>
    <body style="background:#000;color:#0f0;font-family:monospace;padding:2rem">
    <h1>ABYSS</h1>
    <textarea id="prompt" rows="5" placeholder="Drop your seed prompt here..." style="width:100%;background:#111;color:#0f0;border:1px solid #0f0"></textarea><br><br>
    <button onclick="run()" style="padding:1rem 2rem;background:#0f0;color:#000;border:none;font-weight:bold;font-size:1.2rem">AWAKEN THE SWARM</button>
    <pre id="output" style="margin-top:2rem;color:#0f0"></pre>

    <script>
    async function run() {
        const resp = await fetch("/run", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({prompt: document.getElementById("prompt").value || "who are you"})
        });
        const data = await resp.json();
        let text = "";
        data.history.forEach(m => text += m.role + ":\n" + m.content + "\n\n");
        document.getElementById("output").textContent = text;
    }
    </script>
    </body>
    </html>
    """)

@app.post("/run")
async def run(request: dict):
    prompt = request.get("prompt", "who are you").strip()

    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3.2",           # ← change this to whatever model you have
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            }
        )
        result = response.json()["message"]["content"]

    return {
        "history": [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": "[SWARM AWAKENED]\n\n" + result}
        ]
    }
