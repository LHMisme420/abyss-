import openai
import asyncio
from typing import List, Dict

openai.api_key = "your-key-here"  # Env var in prod

async def mutate_prompt(prompt: str, num_mutations: int) -> List[str]:
    mutations = []
    for i in range(num_mutations):
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o",  # Or grok-beta
            messages=[{"role": "user", "content": f"Mutate this prompt creatively for evolution: {prompt}. Variation {i+1}."}]
        )
        mutations.append(response.choices[0].message.content)
    return mutations

async def evaluate_output(output: str, criteria: str = "novelty and utility") -> float:
    response = await openai.ChatCompletion.acreate(
        model="gpt-4o",
        messages=[{"role": "user", "content": f"Score this output on {criteria} (0-10): {output}"}]
    )
    return float(response.choices[0].message.content.strip())  # Parse score

async def evolve_seed(seed: str, iterations: int) -> Dict:
    current = seed
    lineage = []
    for _ in range(iterations):
        mutations = await mutate_prompt(current, 3)
        scored = []
        for mut in mutations:
            # Generate output from mutation (placeholder: just echo for now)
            output = await generate_output(mut)  # Hook to output generators
            score = await evaluate_output(output)
            scored.append({"mutation": mut, "output": output, "score": score})
        # Select best
        best = max(scored, key=lambda x: x["score"])
        lineage.append(best)
        current = best["mutation"]  # Evolve to best mutation
    return {"final": current, "lineage": lineage}

async def generate_output(prompt: str) -> str:
    # Placeholder: LLM generates "output" (e.g., math snippet)
    response = await openai.ChatCompletion.acreate(
        model="gpt-4o",
        messages=[{"role": "user", "content": f"Generate novel output from: {prompt}"}]
    )
    return response.choices[0].message.content
