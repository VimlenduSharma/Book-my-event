###############################################################################
# 1️⃣  Builder – compile wheels
###############################################################################
FROM python:3.12-slim AS builder
WORKDIR /build

RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      build-essential gcc libpq-dev curl \
 && rm -rf /var/lib/apt/lists/*

# ⬅️  Context *is* backend/, so requirements.txt is at top-level
COPY requirements.txt .

RUN pip install --upgrade pip wheel \
 && pip wheel --no-cache-dir --no-deps -r requirements.txt -w /wheels


###############################################################################
# 2️⃣  Runtime – slim image
###############################################################################
FROM python:3.12-slim AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 curl \
 && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH=\"/home/appuser/.local/bin:${PATH}\"

RUN useradd --create-home --shell /bin/bash appuser
USER appuser
WORKDIR /app

# install prebuilt wheels
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*

# ⬅️  Copy *everything* in backend/ into the image
COPY --chown=appuser:appuser . /app

EXPOSE 8000
CMD [\"uvicorn\", \"app.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]
