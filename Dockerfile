FROM python:3.12-slim AS base

# Install minimal deps for security (no dev tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl firejail tini \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code (read-only)
COPY . /app
WORKDIR /app
RUN chmod -R a-w /app/core  # Lock self-mod core files
RUN chown -R 1000:1000 /app

# Firejail profile for child processes (blocks net/forks)
RUN echo '/bin/bash { /etc/firejail/disable-common.inc { include /etc/firejail/disable-programs.inc } netfilter }' > /etc/firejail/abyss.profile

# Tini for proper signal handling
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "main.py"]  # Your FastAPI entrypoint

# Multi-stage for prod: strip debug
FROM base AS prod
RUN pip install --no-cache-dir delocate && find /usr/local -name '*.so' | xargs strip
