"""CrewAI on Maritime: the whole integration is this file.

Maritime speaks to any container through three endpoints (the "BYO
contract", https://maritime.sh/docs/frameworks/custom):

  1. bind 0.0.0.0:$PORT        (PORT is injected; never hardcode 8080)
  2. GET  /health  -> 2xx
  3. POST /chat    -> {"response": "..."} within 30 seconds

Everything else (sleep/wake, per-user VMs, channels, billing) is platform.
"""

import os

from crewai import LLM, Agent, Crew, Task
from fastapi import FastAPI

app = FastAPI()

# Maritime injects OPENAI_API_KEY (a metered proxy token unless you set your
# own) and OPENAI_BASE_URL. Passing both explicitly works on every CrewAI /
# LiteLLM version regardless of which env var spelling it honors.
llm = LLM(
    model=os.getenv("MODEL", "gpt-4o-mini"),
    api_key=os.environ["OPENAI_API_KEY"],
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
    message = body.get("message", "")
    if not message:
        return {"response": "say something and i'll answer"}
    task = Task(
        description=message,
        expected_output="a clear, brief answer to the user's message",
        agent=assistant,
    )
    result = Crew(agents=[assistant], tasks=[task], verbose=False).kickoff()
    return {"response": str(result)}
