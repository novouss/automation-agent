
FROM python:3.11-slim
# Installing uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
# Copy the project into the image
ADD . /app
WORKDIR /app
# Sync the environment with libraries
RUN uv sync
