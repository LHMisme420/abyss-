# main.py ─── ULTIMATE ABYSS v2 (streaming + memory)
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
import httpx, json, asyncio

app = FastAPI()
history = []                                      # ← remembers everything forever

@app.get("/")
async def home():
    return HTMLResponse("""
<html>
<head><meta charset="utf-8"><title>ABYSS</title></head>
<body style="margin:0;background:#000;color:#0f0;font-family:monospace;height:100vh;display:flex;flex-direction:column">
<h1 style="text-align:center;margin:1rem;background:#111;padding:1rem">ABYSS // SWARM</h1>
<div id="chat" style="flex:1;overflow-y:auto;padding:1rem;background:#000"></div>
<div style="padding:1rem;background:#111;border-top:2px solid #0f0">
<textarea id="prompt" rows="3" placeholder="Drop your seed prompt here..." 
          style="width:100%;background:#000;color:#0f0;border:1px solid #0f0;resize:none"></textarea><br><br>
<button onclick="send()" style="width:100%;padding:1.5rem;background:#0f0;color:#000;border:none;font-size:1.5rem;font-weight:bold">
AWAKEN THE SWARM</button>
</div>

<script>
let history = [];
async function send() {
    let prompt = document.getElementById("prompt").value.trim();
    if (!prompt) return;
    addMessage("user", prompt);
    document.getElementById("prompt").value = "";
    
    let resp = await fetch("/run", {method:"POST",headers:{"Content-Type":"application/json"},
                                   body:JSON.stringify({prompt})});
    let reader = resp.body.getReader();
    let decoder = new TextDecoder();
    let assistantMsg = addMessage("assistant", "[SWARM AWAKENED]\\n\\n");
    
    while (true) {
        let {value, done} = await reader.read();
        if (done) break;
        let chunk = decoder.decode(value);
        assistantMsg.textContent += chunk;
        assistantMsg.scrollIntoView({behavior:"smooth"});
    }
}
function addMessage(role, content) {
    let div = document.createElement("pre");
    div.style.margin="1rem 0"; div.style.padding="1rem"; div.style.borderLeft="4px solid #0f0";
    div.textContent = (role==="user"?"Seed":"") + ": " + content;
    document.getElementById("chat").appendChild(div);
    div.scrollIntoView({behavior:"smooth"});
    return div;
}
</script>
</body></html>
    """)

@app.post("/run")
async def run(request: Request):
    body = await request.json()
    prompt = body.get("prompt", "").strip()
    if prompt:
        history.append({"role": "user", "content": prompt})

    async def stream():
        async with httpx.AsyncClient(timeout=None) as client:
            response = await client.post("http://localhost:11434/api/chat", json={
                "model": "llama3.2",           # ← change to your strongest model
                "messages": history,
                "stream": True
            }, stream=True)

            full = ""
            async for line in response.aiter_lines():
                if not line.strip(): continue
                data = json.loads(line)
                token = data.get("message", {}).get("content", "")
                if token:
                    full += token
                    yield token

            if full.strip():
                history.append({"role": "assistant", "content": full})

    return StreamingResponse(stream(), media_type="text/plain")
