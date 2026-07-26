# maritime-crewai-starter

A working [CrewAI](https://crewai.com) agent that deploys to
[Maritime](https://maritime.sh) as-is: per-user micro-VMs, sleep/wake with
memory, channels, and metering, with your crew as the brain.

## Quickstart

1. Fork or clone this repo.
2. Create the agent (dashboard: New Agent -> from GitHub, or API):

```bash
curl -X POST https://api.maritime.sh/api/agents \
  -H "Authorization: Bearer $MARITIME_API_KEY" -H "Content-Type: application/json" \
  -d '{"name": "my-crew", "framework": "crewai",
       "githubRepo": "https://github.com/<you>/maritime-crewai-starter", "branch": "main"}'
```

3. Chat with it from the dashboard, the CLI (`maritime message`), or wire the
   front door so every user of your app gets their own instance.

`CLAUDE.md` in this repo teaches AI coding assistants the platform contract,
so tools like Claude Code can extend this agent without guesswork. Docs:
<https://maritime.sh/docs/frameworks/custom>.

## Layout

- `main.py`: FastAPI wrapper speaking Maritime's 3-endpoint contract + a minimal one-agent crew
- `Dockerfile`: python-slim + ca-certificates + `$PORT` binding
- `CLAUDE.md`: platform contract and recipes for AI coding assistants
