# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI-based Model Context Protocol (MCP) server that provides student services functionality. It demonstrates student financial aid eligibility checking, student profile management, and academic record access through synthetic data. The project uses Python 3.13+ with UV for package management.

## Development Commands

### Setup and Installation
```bash
# Install dependencies
make install
# OR
uv sync
```

### Running the Server
```bash
# Start MCP server locally
make start.mcp
# OR
uv run main.py --host 0.0.0.0 --port 7860 --reload
```

### Testing
```bash
# Run tests
make test
# OR
pytest tests

# Run tests with coverage
make test.coverage
```

### Code Quality
```bash
# Run all quality checks
make lint

# Type checking
make typecheck
# OR
mypy src tests main.py

# Code formatting (check)
make format.check
# OR
black . --check

# Code formatting (apply)
make format.write
# OR
black .

# Linting
make lint.code
# OR
pylint main.py src tests --rcfile=.pylintrc
```

### Docker
```bash
# Build and run with Docker
make build.docker
# OR
docker compose up --build
```

## Architecture

### Core Components

- **FastAPI Application** (`main.py`): Main server with FastAPI-MCP integration
- **Resolvers** (`src/adapters/resolvers/`): Business logic layer that coordinates between different systems
  - `FinancialAidResolver`: Handles financial aid eligibility logic
  - `RegistrarResolver`: Manages student profile and academic data
- **Clients** (`src/adapters/clients/`): Data access layer for different university systems
  - `FinancialAidSystem`: Financial aid business rules
  - `RegistrarSystem`: Student records and synthetic data management
  - `synthetic_data.py`: Generates test data for development
- **Configuration** (`src/config/settings.py`): Pydantic-based settings management with environment variable support
- **Authentication** (`src/middleware/auth.py`): JWT and HuggingFace token validation

### Key Patterns

- **Dependency Injection**: Resolvers are injected into FastAPI endpoints via application state
- **Settings Management**: Uses Pydantic BaseSettings for configuration with environment variable support
- **Authentication**: Supports both JWT tokens (for internal services) and HuggingFace tokens
- **MCP Integration**: Uses fastapi-mcp for Model Context Protocol compatibility

### Data Flow

1. Requests come through FastAPI endpoints
2. Authentication middleware validates tokens
3. Resolvers coordinate between different client systems
4. Clients handle specific business logic and data access
5. Responses are formatted appropriately for MCP consumers

## Configuration

The application uses environment variables for configuration:
- `AUTH_ENABLED`: Enable/disable authentication (default: True)
- `AUTH_TOKEN`: Authentication token
- `HUGGINGFACE_TOKEN`: HuggingFace API token
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 7860)

## Key Files

- `main.py`: FastAPI application entry point
- `src/config/settings.py`: Configuration management
- `src/middleware/auth.py`: Authentication logic
- `src/adapters/resolvers/`: Business logic coordinators
- `src/adapters/clients/`: Data access layer
- `Makefile`: Development commands
- `pyproject.toml`: Python project configuration and dependencies
- `mypy.ini`: Type checking configuration
- `.pylintrc`: Linting configuration

## Testing

The project uses pytest with asyncio support. Test structure follows the source code organization:
- `tests/unit/`: Unit tests
- `tests/integration/`: Integration tests
- `tests/conftest.py`: Test configuration and fixtures

Code coverage target is 80% (excluding client modules).