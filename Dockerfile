# Use Python base image
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Create non-root user (user with uid 1000 is required by HF Spaces)
RUN useradd -m -u 1000 user

# Create app directory and assign ownership
RUN mkdir -p /app && chown -R user:user /app

# Now switch to user (must happen *after* chown if using non-root)
USER user

ENV PATH="/home/user/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy requirements files
COPY --chown=user requirements.txt .
COPY --chown=user uv.lock .
COPY --chown=user pyproject.toml .

# Copy source code
COPY --chown=user ./main.py .
COPY --chown=user ./src ./src
COPY --chown=user ./dist/data ./dist/data

# Create and set up virtual environment
RUN mkdir -p .venv && chown -R user:user .venv
RUN uv venv .venv
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Install dependencies in virtual environment
RUN uv pip install mcp
RUN uv sync --active

# Set environment variables
ENV PORT=7860
ENV PYTHONUNBUFFERED=1

EXPOSE 7860

# Command to run the server
ENTRYPOINT ["uv", "run", "main.py"]
