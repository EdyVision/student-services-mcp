---
title: Student Services MCP Server
emoji: 🧾
colorFrom: blue
colorTo: green
sdk: docker
sdk_version: "1.0"
app_file: Dockerfile
pinned: false
---

# Student Services MCP Server
<div align=center>

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
[![Medium](https://img.shields.io/badge/Medium-12100E?style=for-the-badge&logo=medium&logoColor=white)](https://medium.com/@docejr/experimenting-with-a-demo-mcp-and-gemini-e5b183e3b3f3)
[![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=for-the-badge&logo=kaggle&logoColor=white)](https://www.kaggle.com/code/edyvision/5dgai-gemini-demo-student-services-mcp)
</div>

This is a FastAPI-MCP based server that provides student services functionality through an MCP (Model Control Protocol) interface. The server allows you to manage and check student financial aid eligibility. It was built as part of the 5-Day Google AI Kaggle Competition / Course in Q1 of 2025. Check out the <a href="https://medium.com/@docejr/experimenting-with-a-demo-mcp-and-gemini-e5b183e3b3f3">Medium</a> post or <a href="https://www.kaggle.com/code/edyvision/5dgai-gemini-student-services-agent-mcp">Kaggle notebook</a> for full submission details.

It demonstrates how to:

- Fetch student profiles and academic history
- Determine financial aid eligibility based on academic performance and field of study
- Handle synthetic data for demonstration purposes

## Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) - A fast Python package installer and resolver
- [Docker](https://www.docker.com/) (optional, for containerized deployment)


## Features

- Fetch student information
- Check student eligibility for financial aid
- Manage student records
- Real-time eligibility updates

## API Endpoints

The server exposes the following main endpoints:
- `/messages/` - Main endpoint for all MCP operations
- `/mcp` - Server-Sent Events endpoint for real-time updates

## Available Commands

1. `fetch_students` - Retrieves a list of all students
2. `check_financial_aid_eligibility <student_id>` - Checks financial aid eligibility for a specific student
3. `fetch_student <student_id>` - Retrieves detailed information for a specific student

## Development

The server uses:
- FastAPI for the web framework
- UV for Python package management
- MCP for the protocol implementation

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/edyvision/student-services-demo-mcp.git
cd student-services-demo-mcp
```

2. Install dependencies:
```bash
uv sync

# or

make install
```

3. Run the server:
```bash
uv run main.py

#or 

make start.mcp
```

4. Connecting with Custom Client or Agent
A simple Python client is provided to interact with the server. The client is located in `src/client.py`. Here's how to use it:

```python
from src.client import StudentServicesMCPClient

# Create a client instance
client = StudentServicesMCPClient()

# Connect
await client.connect_to_server()

# Fetch students
students = await client.fetch_students(limit: int = <limit>)

# Check eligibility for a specific student
student_id = "<student_id>"
eligibility = await client.check_financial_aid_eligibility(student_id)

# Fetch details for a specific student
student_details = await client.fetch_student(student_id)
```

## Docker Setup

### Building the Image and Running Container

```bash
docker compose up --build
```

The server will be available at `http://localhost:7860`

## Deployment
This project deploys to HuggingFace. Simply create a new HuggingFace Space, update the Makefile with your space URL, then run the following:

```bash
make hf.deploy
```

## Connecting to Cursor
To connect Cursor to either your local or HF deployed space, update the mcp.json file to include the following:

```json
{
  "mcpServers": {
    "student-services-mcp-hf": {
      "url": "https://<hf_user-handle>-student-services-demo-mcp.hf.space/mcp",
      "headers": {
        "Authorization": "Bearer ${HF_TOKEN}",
        "Accept": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive"
      }
    },
    "student-services-mcp-local": {
      "url": "http://0.0.0.0:7860/mcp"
    }
  }
}
```