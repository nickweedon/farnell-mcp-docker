# Farnell MCP Server Dockerfile
# Multi-stage build with manual file filtering for production

# Stage 1: Copy all source files (no .dockerignore filtering)
FROM python:3.12-slim AS source

WORKDIR /source
COPY . .

# Stage 2: Filter files for production (remove dev-only files)
FROM python:3.12-slim AS filtered-source

WORKDIR /filtered

# Copy from source and manually filter out development files
COPY --from=source /source /filtered

# Remove development-only files and directories
RUN rm -rf \
    # Git
    .git \
    .gitignore \
    # Python artifacts
    __pycache__ \
    *.py[cod] \
    *.egg-info \
    .eggs \
    dist \
    build \
    *.egg \
    # Virtual environments
    .venv \
    venv \
    # Testing
    .pytest_cache \
    .coverage \
    htmlcov \
    tests \
    # IDEs
    .idea \
    .vscode \
    # Documentation (keep README.md)
    docs \
    CLAUDE.md \
    # Environment files
    .env \
    .env.local \
    .env.*.local \
    # Docker files
    Dockerfile* \
    docker-compose*.yml \
    .docker \
    dockerignore.reference \
    # Dev container
    .devcontainer \
    # Claude
    .claude \
    # Logs
    *.log \
    logs \
    # Temporary files
    tmp \
    temp \
    *.tmp \
    *.bak

# Stage 3: Base production image
FROM python:3.12-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy filtered production files
COPY --from=filtered-source /filtered /app

# Install production dependencies
RUN uv sync --frozen --no-dev 2>/dev/null || uv sync --no-dev

# Stage 4: Production stage
FROM base AS production
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["uv", "run", "farnell-mcp"]

# Stage 5: Development stage with all files and additional tools
FROM python:3.12-slim AS development

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy ALL files from source (including tests, CLAUDE.md, etc.)
COPY --from=source /source /app

# Install Node.js for Claude Code CLI
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI
RUN npm install -g @anthropic-ai/claude-code

# Install dev dependencies (including optional dev dependencies)
RUN uv sync --frozen --all-extras 2>/dev/null || uv sync --all-extras

ENV PYTHONUNBUFFERED=1
CMD ["bash"]
