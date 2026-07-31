FROM python:3.11-slim

# ffmpeg backs audio decoding for voice notes. Skip it only if you run with
# STT_BACKEND=none.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY scripts/ ./scripts/

ENV PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1 \
    DATABASE_PATH=/data/myway.db \
    HF_HOME=/models

# SQLite lives in /data; whisper weights are cached in /models so a container
# restart doesn't re-download them.
VOLUME ["/data", "/models"]

RUN useradd --create-home --uid 10001 myway \
    && mkdir -p /data /models \
    && chown -R myway:myway /data /models
USER myway

# Fail fast on a malformed corpus rather than at the first user's verdict.
HEALTHCHECK --interval=60s --timeout=15s --start-period=20s --retries=3 \
    CMD python -c "import sys; sys.path.insert(0,'/app/src'); from myway.science import Library; Library()"

CMD ["python", "-m", "myway"]
