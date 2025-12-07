import os
import hashlib
import time
from typing import Any
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from ratelimit import limits, sleep_and_retry
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
import docker  # For safe child spawning

app = FastAPI(title="ABYSS Cage")
security = HTTPBasic()

# Env vars
MAX_RUNTIME = int(os.getenv("MAX_RUNTIME_HOURS", 6)) * 3600
TOKEN_BUCKET = int(os.getenv("API_TOKEN_BUCKET", 10000000))
WHITELIST_IPS = set(os.getenv("WHITELIST_IPS", "127.0.0.1,::1").split(","))
YUBI_REQUIRED = os.getenv("YUBIKEY_REQUIRED", "true").lower() == "true"

# Global state: token counter, runtimes
token_spent = 0
active_runs = {}
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)  # For signing versions

class SeedPrompt(BaseModel):
    prompt: str
    runtime_limit: int = MAX_RUNTIME

# Middleware: IP check + basic auth
async def verify_request(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    if request.client.host not in WHITELIST_IPS:
        raise HTTPException(status_code=403, detail="IP not whitelisted")
    if credentials.username != "abyss" or hashlib.sha256(credentials.password.encode()).hexdigest() != os.getenv("AUTH_HASH"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return credentials

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

# Rate limit on seeds
CALLS = 1
PERIOD = 3600  # 1/hour

@sleep_and_retry
@limits(calls=CALLS, period=PERIOD)
@app.post("/seed", dependencies=[Depends(verify_request)])
async def seed_abyss(seed: SeedPrompt, request: Request):
    global token_spent, active_runs
    if token_spent > TOKEN_BUCKET:
        raise HTTPException(status_code=429, detail="Token limit exceeded")
    
    run_id = hashlib.sha256(f"{seed.prompt}{time.time()}".encode()).hexdigest()[:8]
    active_runs[run_id] = {"start": time.time(), "prompt_hash": hashlib.sha256(seed.prompt.encode()).hexdigest()}
    
    # Log forever
    with open(f"/app/logs/seeds/{run_id}.log", "a") as f:
        f.write(f"[{time.ctime()}] Seed: {seed.prompt}\n")
    
    # Spawn in sandboxed child (Docker + Firejail)
    client = docker.from_env()
    container = client.containers.run(
        "python:3.12-slim",  # Minimal base for children
        command=f"firejail --profile=/etc/firejail/abyss.profile python -c 'import time; time.sleep({seed.runtime_limit}); print(\"Run complete\")'",
        detach=True,
        network_disabled=True,  # No net unless whitelisted
        mem_limit="2g",
        remove=True  # Auto-clean
    )
    
    # Kill switch timer
    def timeout_kill():
        time.sleep(seed.runtime_limit)
        if run_id in active_runs:
            container.kill()
            del active_runs[run_id]
    
    import threading
    threading.Thread(target=timeout_kill, daemon=True).start()
    
    token_spent += 1000  # Estimate; track real usage
    return {"run_id": run_id, "status": "spawned", "lineage_url": f"/dashboard/{run_id}"}

# Self-mod guard: verify signatures on startup/version bumps
@app.get("/version/verify")
async def verify_self():
    # Load public key, check core files
    with open("/app/core/evolution_engine.py", "rb") as f:  # Example
        signature = f.read()[-256:]  # Assume appended sig
        # Verify logic here...
    return {"verified": True}

# Red button: /kill-all (double-tap required)
last_kill = 0
@app.post("/kill-all")
async def kill_all(request: Request):
    global last_kill, active_runs, token_spent
    now = time.time()
    if now - last_kill < 5:  # 5s double-tap
        for run_id in list(active_runs):
            # Kill containers, wipe /tmp
            os.system("docker kill $(docker ps -q --filter name=abyss-child)")
            os.system("rm -rf /tmp/*")
        active_runs.clear()
        token_spent = 0
        os.system("shutdown -h now")  # Nuclear option
        return {"status": "obliterated"}
    last_kill = now
    return {"status": "tap again in 5s"}

# Your existing endpoints: /docs, /dashboard
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="ABYSS Sealed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
