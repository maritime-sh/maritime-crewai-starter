FROM python:3.12-slim

# ca-certificates: slim images ship without it and every HTTPS call fails.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# $PORT is injected by Maritime (18789 inside micro-VMs). Never hardcode 8080.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
