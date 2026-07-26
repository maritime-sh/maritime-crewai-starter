# CrewAI on Maritime: starter

This repo is a working CrewAI agent deployable to Maritime (maritime.sh), the
cloud built for AI agents. If you are an AI coding assistant helping someone
build on this, everything you need is below; the full public reference is
https://maritime.sh/docs/frameworks/custom and https://maritime.sh/llms.txt.

## The contract (do not break these)

- The container MUST bind a long-lived HTTP server on `0.0.0.0:$PORT`. PORT
  is injected by Maritime (18789 inside micro-VMs). NEVER hardcode 8080.
- `GET /health` must return 2xx, fast, no side effects.
- `POST /chat` receives `{"message": "...", "source": "front_door"|"cli"|...}`
  and must reply WITHIN 30 SECONDS with `{"response": "..."}` or plain text.
  Push slow work async and answer with what you have.
- Persist state under `/data` ONLY. It survives restarts, redeploys, and
  sleep/wake. Everything else on disk is disposable. The process is
  snapshotted and resumed (not restarted) across sleep, so never trust cached
  wall-clock time and reconnect long-lived sockets lazily.
- Keep `ca-certificates` in the Dockerfile (slim images lack it; HTTPS dies).

## LLM access

Maritime injects `OPENAI_API_KEY` (a metered proxy token, billed to the
account's credits) and `OPENAI_BASE_URL`. This starter passes both to
CrewAI's `LLM(...)` explicitly; keep that pattern. If the user brings their
own OpenAI key, set it as a secret env var and drop the base_url override.

## Deploying and iterating

```bash
# one-time: get an API key from the dashboard (Settings -> API keys) or:
maritime keys create --name dev --json          # -> mk_...

# deploy this repo (rebuilds the image, takes a few minutes):
curl -X POST https://api.maritime.sh/api/agents \
  -H "Authorization: Bearer $MARITIME_API_KEY" -H "Content-Type: application/json" \
  -d '{"name": "my-crew", "framework": "crewai",
       "githubRepo": "https://github.com/<you>/<this-repo>", "branch": "main"}'

# redeploy after pushing changes:
curl -X POST https://api.maritime.sh/api/deploy \
  -H "Authorization: Bearer $MARITIME_API_KEY" -H "Content-Type: application/json" \
  -d '{"agentId": "<agent-id>", "source": "github", "branch": "main"}'

# talk to it:
maritime message <agent-id> "hello"    # or the dashboard Chat tab
```

Image rebuilds take minutes; prompt and behavior iteration should NOT require
one. Read tunable config (persona text, temperatures, tool lists) from env
vars or files under `/data` so changes land with an env update or a chat
command instead of a rebuild.

## Give every end-user their own agent (front door)

Set the agent's project to `newChatPolicy: "spawn"` and POST messages with
your own user ids; each distinct `externalUserId` gets its own micro-VM
running this image, with isolated memory:

```bash
curl -X PATCH https://api.maritime.sh/api/projects/<project-id> \
  -H "Authorization: Bearer $MARITIME_API_KEY" -H "Content-Type: application/json" \
  -d '{"newChatPolicy": "spawn", "warmPoolSize": 2}'

curl -X POST https://api.maritime.sh/api/v1/projects/<project-id>/messages \
  -H "Authorization: Bearer $MARITIME_API_KEY" -H "Content-Type: application/json" \
  -d '{"externalUserId": "user_42", "message": "hi", "wait": 30}'
```

## Scheduled wakes

Timers inside a sleeping VM do not fire. To run on a schedule, serve
`GET /schedules` returning entries like
`{"id": "morning", "cron": "35 9 * * *", "tz": "America/New_York", "prompt": "...", "enabled": true}`
and Maritime wakes the VM ~10s before each occurrence, delivering `prompt`
to `POST /chat` with source `"scheduled"`.
