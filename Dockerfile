FROM node:22-slim AS dependencies
WORKDIR /fixture
COPY dependency-lock .
RUN node -e 'const fs = require("fs"); const crypto = require("crypto"); const ITERATIONS = 500000; const KEY_BYTES = 32; const input = fs.readFileSync("dependency-lock"); fs.writeFileSync("dependency-proof", crypto.pbkdf2Sync(input, "staging-cache-fixture", ITERATIONS, KEY_BYTES, "sha256").toString("hex"));'
FROM node:22-slim
COPY --from=dependencies /fixture/dependency-proof /dependency-proof
COPY source-marker /source-marker
CMD ["sleep", "infinity"]
