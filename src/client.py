import asyncio
from typing import Optional
from contextlib import AsyncExitStack
import os
from dotenv import load_dotenv

from mcp import ClientSession
from mcp.client.sse import sse_client

load_dotenv()  # load environment variables from .env


class FinaidMCPClient:
    def __init__(self, base_url: str = "http://localhost:7860/sse"):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.base_url = base_url

    async def connect_to_server(self):
        """Connect to the Hugging Face Space MCP server"""
        # Initialize SSE transport
        sse_transport = await self.exit_stack.enter_async_context(
            sse_client(
                url=self.base_url,
                # headers={"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
            )
        )

        # Create client session with the SSE transport
        read_stream, write_stream = sse_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def fetch_students(self, limit: int = 100):
        """Fetch a list of students"""
        response = await self.session.call_tool("fetch_students", {"limit": limit})
        return response.content

    async def check_financial_aid_eligibility(self, student_id: str):
        """Check financial aid eligibility for a student"""
        response = await self.session.call_tool(
            "check_financial_aid_eligibility", {"student_id": student_id}
        )
        return response.content

    async def fetch_student_profile(self, student_id: str):
        """Fetch a student's profile"""
        response = await self.session.call_tool(
            "fetch_student_profile", {"student_id": student_id}
        )
        return response.content

    async def fetch_academic_history(self, student_id: str):
        """Fetch a student's academic history"""
        response = await self.session.call_tool(
            "fetch_academic_history", {"student_id": student_id}
        )
        return response.content

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()
