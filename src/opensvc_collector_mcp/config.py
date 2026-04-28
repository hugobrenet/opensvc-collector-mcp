import os

from dotenv import load_dotenv


load_dotenv()


OPENSVC_USER = os.getenv("OPENSVC_USER")
OPENSVC_PASSWORD = os.getenv("OPENSVC_PASSWORD")
OPENSVC_API_BASE_URL = os.getenv("OPENSVC_API_BASE_URL")
MCP_PORT = os.getenv("MCP_PORT")

HTTP_REQUEST_TIMEOUT_SECONDS = 20.0
TOOL_TIMEOUT_SECONDS = 90.0
