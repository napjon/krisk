import os
import sys
from pathlib import Path

import httpx
import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamable_http_client

from krisk.server import create_app
from krisk.service import KriskService
from krisk.sources import SourceRegistry
from krisk.storage import ArtifactStore, MemoryRepository


@pytest.fixture
def mcp_service(tmp_path):
    return KriskService(
        SourceRegistry(),
        MemoryRepository(),
        ArtifactStore(tmp_path / "artifacts"),
    )


@pytest.mark.asyncio
async def test_streamable_http_mcp_client_lists_and_calls_tools(mcp_service):
    app = create_app(mcp_service)
    mcp = app.state.krisk_mcp
    async with mcp.session_manager.run():
        transport = httpx.ASGITransport(app=app)
        async with (
            httpx.AsyncClient(
                transport=transport,
                base_url="http://127.0.0.1:8060",
            ) as http_client,
            streamable_http_client(
                "http://127.0.0.1:8060/mcp/",
                http_client=http_client,
            ) as (read, write, _),
            ClientSession(read, write) as session,
        ):
            initialized = await session.initialize()
            tools = await session.list_tools()
            result = await session.call_tool("list_sources", {})

    assert initialized.serverInfo.name == "Krisk Living Research"
    assert {tool.name for tool in tools.tools} >= {
        "list_sources",
        "run_query",
        "create_chart",
        "save_research",
    }
    assert not result.isError


@pytest.mark.asyncio
async def test_stdio_mcp_client_lists_tools(tmp_path):
    environment = dict(os.environ)
    environment["KRISK_DATABASE_PATH"] = str(tmp_path / "krisk.db")
    parameters = StdioServerParameters(
        command=sys.executable,
        args=["-m", "krisk.cli", "mcp"],
        cwd=str(Path.cwd()),
        env=environment,
    )
    async with stdio_client(parameters) as (read, write), ClientSession(read, write) as session:
        initialized = await session.initialize()
        tools = await session.list_tools()

    assert initialized.serverInfo.name == "Krisk Living Research"
    assert len(tools.tools) >= 8
