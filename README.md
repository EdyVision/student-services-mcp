---
title: Financial Aid MCP Server
emoji: 🧾
colorFrom: blue
colorTo: green
sdk: docker
sdk_version: "1.0"
app_file: Dockerfile
pinned: false
---

# Financial Aid MCP Server

This is a FastAPI-based server that provides financial aid management functionality through an MCP (Model Control Protocol) interface. The server allows you to manage and check student financial aid eligibility.

## Features

- Fetch student information
- Check student eligibility for financial aid
- Manage student records
- Real-time eligibility updates

## API Endpoints

The server exposes the following main endpoints:
- `/messages/` - Main endpoint for all MCP operations
- `/sse` - Server-Sent Events endpoint for real-time updates

## Available Commands

1. `fetch_students` - Retrieves a list of all students
2. `check_financial_aid_eligibility <student_id>` - Checks financial aid eligibility for a specific student
3. `fetch_student <student_id>` - Retrieves detailed information for a specific student

## Docker Setup

### Building the Image

```bash
docker build -t finaid-mcp .
```

### Running the Container

```bash
docker run -p 7860:7860 finaid-mcp
```

The server will be available at `http://localhost:7860`

## Python Client

A simple Python client is provided to interact with the server. The client is located in `src/client.py`. Here's how to use it:

```python
from src.client import FinaidClient

# Create a client instance
client = FinaidClient()

# Fetch all students
students = client.fetch_students()

# Check eligibility for a specific student
student_id = "df62674f-5641-4657-a614-901a22ea76f2"
eligibility = client.check_financial_aid_eligibility(student_id)

# Fetch details for a specific student
student_details = client.fetch_student(student_id)
```

## Development

The server uses:
- FastAPI for the web framework
- UV for Python package management
- MCP for the protocol implementation

### Local Development

1. Install dependencies:
```bash
uv sync
```

2. Run the server:
```bash
uv run main.py
```

3. Connecting with Custom Client
```python
from src.client import FinaidMCPClient

client = FinaidMCPClient()  # defaults to localhost, pass in your huggingface space

try:
    await client.connect_to_server()

    # Example: Fetch students
    students = await client.fetch_students(limit=10)
    print("First 10 students:")
    for student in students:
        print(f"- {student['name']} (GPA: {student['gpa']})")

    # Example: Check financial aid eligibility
    student_id = "0c1a6fd7-c426-451d-a047-ae74cf091863"
    eligibility = await client.check_financial_aid_eligibility(student_id)
    print(f"\nEligibility for student {student_id}:")
    print(eligibility)

finally:
    await client.cleanup()
```

## Environment Variables

- `PORT` - Server port (default: 7860)
- `PYTHONUNBUFFERED` - Python output buffering (default: 1)