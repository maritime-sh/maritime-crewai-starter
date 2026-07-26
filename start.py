"""Entrypoint. On Maritime micro-VMs the image CMD is re-executed by the VM
init as a flattened string, so shell-quoted forms like
`sh -c "uvicorn ... --port $PORT"` lose their argument boundaries and crash
the boot. Launching from Python sidesteps shell quoting entirely.
"""

import os

import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
