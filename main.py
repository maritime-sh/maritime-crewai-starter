"""CrewAI on Maritime: the whole integration is this file.

Maritime speaks to any container through three endpoints (the "BYO
contract", https://maritime.sh/docs/frameworks/custom):

  1. bind 0.0.0.0:$PORT        (PORT is injected; never hardcode 8080)
  2. GET  /health  -> 2xx
  3. POST /chat    -> {"response": "..."} within 30 seconds

Everything else (sleep/wake, per-user VMs, channels, billing) is platform.
"""

import asyncio
import os

from crewai import LLM, Agent, Crew, Task
from fastapi import FastAPI

app = FastAPI()

# Maritime injects OPENAI_API_KEY (a metered proxy token unless you set your
# own) and OPENAI_BASE_URL. Passing both explicitly works on every CrewAI /
# LiteLLM version regardless of which env var spelling it honors. Never crash
# at import when the key is missing: this process is PID 1 in a micro-VM, and
# an import crash means a kernel panic boot loop instead of a useful error.
_api_key = os.getenv("OPENAI_API_KEY", "")
assistant = None
if _api_key:
    llm = LLM(
        model=os.getenv("MODEL", "gpt-4o-mini"),
        api_key=_api_key,
        base_url=os.getenv("OPENAI_BASE_URL") or None,
    )
    assistant = Agent(
        role="helpful assistant",
        goal="answer the user's message clearly and briefly",
        backstory="You are a concise, friendly assistant running as a Maritime agent.",
        llm=llm,
        verbose=False,
    )


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/chat")
async def chat(body: dict):
    if assistant is None:
        return {"response": "no OPENAI_API_KEY is set for this agent; add one in the dashboard (Environment tab) and restart"}
    message = body.get("message", "")
    if not message:
        return {"response": "say something and i'll answer"}
    task = Task(
        description=message,
        expected_output="a clear, brief answer to the user's message",
        agent=assistant,
    )
    crew = Crew(agents=[assistant], tasks=[task], verbose=False)
    # kickoff() is synchronous and refuses to run inside FastAPI's event
    # loop; a worker thread keeps this version-proof.
    result = await asyncio.to_thread(crew.kickoff)
    return {"response": str(result)}


@app.get("/schedules")
def schedules():
    # Maritime polls this to register wake triggers for scheduled work.
    # Return entries like {"id": "morning", "cron": "35 9 * * *",
    # "tz": "UTC", "prompt": "...", "enabled": true} when you have some.
    return []
