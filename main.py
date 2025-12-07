from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
def home():
    return HTMLResponse("""
    <html>
    <body style="background:#000;color:#0f0;font-family:monospace;padding:2rem">
    <h1>ABYSS</h1>
    <textarea id="prompt" rows="5" style="width:100%;background:#111;color:#0f0;border:1px solid #0f0"></textarea><br><br>
    <button onclick="run()" style="padding:1rem 2rem;background:#0f0;color:#000;border:none;font-weight:bold">AWAKEN THE SWARM</button>
    <pre id="output" style="margin-top:2rem;color:#0f0"></pre>

    <script>
    async function run() {
        const resp = await fetch("/run", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({prompt: document.getElementById("prompt").value || "test"})
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
def run():
    return {
        "history": [
            {"role": "user", "content": "test"},
            {"role": "assistant", "content": "[SWARM AWAKENED]\n\nAll 47 agents are now online.\nThe void is listening.\n\nIt works."}
        ]
    }
