---
title: Student Services MCP Server
tags: 
- mcp
- fictitious
- education
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
![](https://badge.mcpx.dev?type=server 'MCP Server')
[![Medium](https://img.shields.io/badge/Medium-12100E?style=for-the-badge&logo=medium&logoColor=white)](https://medium.com/@docejr/experimenting-with-a-demo-mcp-and-gemini-e5b183e3b3f3)
[![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=for-the-badge&logo=kaggle&logoColor=white)](https://www.kaggle.com/code/edyvision/5dgai-gemini-demo-student-services-mcp)
</div>

This is a FastAPI-MCP based server that provides comprehensive student services functionality through an MCP (Model Control Protocol) interface. The server allows you to manage student records, check financial aid eligibility, perform academic planning, and conduct advanced analytics including attrition prediction and dropout risk analysis. It was built as part of the `5-Day Google AI Kaggle Competition / Course` in Q1 of 2025 and has since been expanded to support the new `Academic Planning Agent` sample project and advanced student analytics.

For the original agent concept, check out the <a href="https://medium.com/@docejr/experimenting-with-a-demo-mcp-and-gemini-e5b183e3b3f3">Medium</a> post or <a href="https://www.kaggle.com/code/edyvision/5dgai-gemini-student-services-agent-mcp">Kaggle notebook</a> for full submission details.

For the new Academic Planning Assistant, check out <a href="https://github.com/EdyVision/academic-planning-assistant.git">Academic Planning Assistant Project</a>.

It demonstrates how to:

- Fetch student profiles and academic history
- Determine financial aid eligibility based on academic performance and field of study
- Generate and manage academic course plans
- Submit and track student notes and observations
- Predict student dropout risk using machine learning
- Analyze attrition patterns and feature importance
- Identify high-risk students for early intervention
- Handle synthetic data for demonstration purposes

## Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) - A fast Python package installer and resolver
- [Docker](https://www.docker.com/) (optional, for containerized deployment)


## Features

### Core Student Management
- Fetch student information and profiles
- Retrieve academic history and records
- Manage student data and notes

### Financial Aid System
- Check student eligibility for financial aid
- Real-time eligibility updates
- Support for merit-based and need-based aid

### Academic Planning
- Generate personalized course plans
- Submit and track academic plans
- Stress-level aware planning

### Advanced Analytics & Attrition Prediction
- **Dropout Risk Prediction**: ML-based risk assessment for individual students
- **High-Risk Student Identification**: Automated flagging of at-risk students
- **Attrition Statistics**: Comprehensive population-level analytics
- **Feature Importance Analysis**: Understanding key predictors of student success
- **Attrition Factor Analysis**: Detailed breakdown of risk factors per student

## API Endpoints

The server exposes the following main endpoints:
- `/messages/` - Main endpoint for all MCP operations
- `/mcp` - Server-Sent Events endpoint for real-time updates

## Available Commands

### Student Management
1. `fetch_students` - Retrieves a list of all students
2. `fetch_student_profile <student_id>` - Retrieves detailed information for a specific student
3. `fetch_student_profile_by_name <student_name>` - Retrieves student profile by name (case-insensitive)
4. `fetch_academic_history <student_id>` - Retrieves academic history for a student

### Financial Aid
5. `fetch_financial_aid_eligibility <student_id>` - Checks financial aid eligibility for a specific student

### Academic Planning
6. `fetch_course_plan <student_id> <target_credits> <stress_level>` - Generates a course plan for a student
7. `submit_course_plan <student_id> <plan> <justification>` - Submits a course plan with justification

### Student Notes
8. `submit_note <student_id> <note> <stress_level>` - Submits a note for a student

### Analytics & Attrition Prediction
9. `fetch_student_dropout_risk <student_id>` - Get dropout risk prediction for a specific student
10. `fetch_high_risk_students <limit>` - Get list of students at high risk of dropping out
11. `fetch_attrition_statistics` - Get overall attrition statistics for the student population
12. `fetch_student_attrition_analysis <student_id>` - Get detailed attrition factor analysis for a student
13. `fetch_attrition_feature_importance` - Get feature importance analysis for dropout prediction

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

# Student Management
students = await client.fetch_students(limit=50)
student_profile = await client.fetch_student_profile("S001")
academic_history = await client.fetch_academic_history("S001")

# Financial Aid
eligibility = await client.fetch_financial_aid_eligibility("S001")

# Academic Planning
course_plan = await client.fetch_course_plan("S001", target_credits=15, stress_level="moderate")
await client.submit_course_plan("S001", "Plan details...", "Justification...")

# Student Notes
await client.submit_note("S001", "Student struggling with math", "high")

# Analytics & Attrition Prediction
dropout_risk = await client.fetch_student_dropout_risk("S001")
high_risk_students = await client.fetch_high_risk_students(limit=10)
attrition_stats = await client.fetch_attrition_statistics()
attrition_analysis = await client.fetch_student_attrition_analysis("S001")
feature_importance = await client.fetch_attrition_feature_importance()
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
