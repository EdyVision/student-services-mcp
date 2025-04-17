import asyncio
from typing import Optional, Dict
from contextlib import AsyncExitStack
import os
from dotenv import load_dotenv

from mcp import ClientSession
from mcp.client.sse import sse_client

load_dotenv()  # load environment variables from .env


class StudentServicesMCPClient:
    def __init__(self, base_url: str = "http://localhost:7860/mcp"):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.base_url = base_url
        self.base_headers = {
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
        self.hf_token = os.getenv("HF_TOKEN")

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get headers including authentication if token is available"""
        headers = self.base_headers.copy()
        if self.hf_token:
            headers["Authorization"] = f"Bearer {self.hf_token}"
        return headers

    async def connect_to_server(self):
        """Connect to the Hugging Face Space MCP server"""
        try:
            print(f"\nConnecting to server at: {self.base_url}")
            # Initialize SSE transport with headers
            sse_transport = await self.exit_stack.enter_async_context(
                sse_client(
                    url=self.base_url,
                    headers=self._get_auth_headers(),
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
        except Exception as e:
            print(f"Error connecting to server: {e}")
            raise

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
