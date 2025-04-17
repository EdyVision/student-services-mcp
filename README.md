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

# Student Services Demo MCP

A demonstration of a Multi-Component Platform (MCP) for student services, including financial aid eligibility determination.

## Overview

This project showcases a Multi-Component Platform (MCP) that integrates student records and financial aid systems. It demonstrates how to:

- Fetch student profiles and academic history
- Determine financial aid eligibility based on academic performance and field of study
- Handle synthetic data for demonstration purposes

## Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) - A fast Python package installer and resolver
- [Docker](https://www.docker.com/) (optional, for containerized deployment)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/student-services-demo-mcp.git
cd student-services-demo-mcp
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies using uv:
```bash
uv pip install -r requirements.txt
```

## Usage

### Local Development

1. Start the server:
```bash
make run
```

2. In a separate terminal, run the example notebook:
```bash
make notebook
```

### Hugging Face Space Deployment

1. Create a new Hugging Face Space
2. Configure the space with the following environment variables:
   - `HOST`: The host to bind to (default: 0.0.0.0)
   - `PORT`: The port to listen on (default: 7860)
   - `HF_SPACE_URL`: The URL of your Hugging Face Space

3. Deploy the space using the Hugging Face CLI or web interface

## Example Usage

```python
from src.client import FinaidMCPClient

# Initialize the client
client = FinaidMCPClient(base_url="http://localhost:7860/mcp")  # or your Hugging Face Space URL

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

## Makefile
All commands presented here have a Makefile equivalent.

- `PORT` - Server port (default: 7860)
- `PYTHONUNBUFFERED` - Python output buffering (default: 1)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## API Endpoints

The server exposes the following main endpoints:
- `/messages/` - Main endpoint for all MCP operations
- `/mcp` - Server-Sent Events endpoint for real-time updates

## Available Commands

1. `fetch_students` - Retrieves a list of all students
2. `check_financial_aid_eligibility <student_id>` - Checks financial aid eligibility for a specific student
3. `fetch_student <student_id>` - Retrieves detailed information for a specific student

## Docker Setup

### Building the Image

```bash
docker build -t student-services-demo-mcp .
```

### Running the Container

```bash
docker run -p 7860:7860 student-services-demo-mcp
```

The server will be available at `http://localhost:7860`

## Python Client

A simple Python client is provided to interact with the server. The client is located in `src/client.py`. Here's how to use it:

```python
from src.client import StudentServicesMCPClient

# Create a client instance
client = StudentServicesMCPClient()

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

3. Connecting with Custom Client or Agent

## Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) - A fast Python package installer and resolver
- [Docker](https://www.docker.com/) (optional, for containerized deployment)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/student-services-demo-mcp.git
cd student-services-demo-mcp
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies using uv:
```bash
uv pip install -r requirements.txt
```