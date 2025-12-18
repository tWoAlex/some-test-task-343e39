FROM ghcr.io/astral-sh/uv:python3.14-alpine
COPY pyproject.toml uv.lock /
RUN uv sync
WORKDIR /
ADD ./app /app/
EXPOSE 8000
CMD ["/bin/sh", "-c", "uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 & uv run celery -A app.celery.main worker -P eventlet"]
