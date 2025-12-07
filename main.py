from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from evolution_engine import evolve_seed  # We'll build this next
from persistence import init_db, add_lineage_entry
from scheduler import start_autonomy_loop

app = FastAPI(title="ABYSS", version="0.1.2")

class SeedPrompt(BaseModel):
    prompt: str
    iterations: int = 3  # Default mutations

@app.post("/seed")
async def submit_seed(seed: SeedPrompt):
    try:
        # Evolve the seed
        results = await evolve_seed(seed.prompt, seed.iterations)
        # Log to lineage
        lineage_id = add_lineage_entry(seed.prompt, results)
        return {"status": "evolved", "lineage_id": lineage_id, "outputs": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard")
async def dashboard():
    # Fetch lineage tree from DB
    tree = get_lineage_tree()  # Implement in persistence.py
    return {"lineage": tree}

@app.on_event("startup")
async def startup_event():
    init_db()
    start_autonomy_loop()  # Kicks off background evolution

if __name__ == "__main__":
    # Check for public IP warning
    import os
    if os.getenv("PUBLIC_IP", "false").lower() == "true":
        print("WARNING: Running on public IP. Proceed with caution.")
    uvicorn.run(app, host="0.0.0.0", port=8000)
