FROM python:3.12-slim

# ca-certificates: slim images ship without it and every HTTPS call fails.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# $PORT is injected by Maritime (18789 inside micro-VMs). Never hardcode 8080,
# and never use a shell-string CMD (sh -c "...") — micro-VM init flattens the
# CMD to one string, so nested quoting breaks. start.py reads $PORT itself.
CMD ["python", "start.py"]
