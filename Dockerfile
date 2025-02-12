
FROM python:3.13-slim-bookworm
# Installing uv
COPY --from=ghcr.io/astral-sh/uv:0.5.30 /uv /uvx /bin/
# Copy the project into the image
ADD . /app
WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"
# Sync the environment with libraries
RUN uv sync --frozen
CMD ["/app/.venv/bin/uvicorn", "app:app", "--port", "8000", "--host", "0.0.0.0"]
