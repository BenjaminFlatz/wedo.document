FROM python:3.11-slim

WORKDIR /app

# setuptools' package discovery (packages.find, where=["src"]) needs the
# src/ tree present at install time, so copy everything before installing
# rather than relying on a pyproject-only caching layer.
COPY pyproject.toml ./
COPY src ./src

RUN pip install --no-cache-dir -e .

# Persisted SQLite database lives here; mount a volume at this path in
# production so data survives redeploys.
RUN mkdir -p /app/data

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

# Railway injects $PORT; default to 8000 for local `docker run`.
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
