import asyncio
from pathlib import Path

from mcp import Client

from frankenstein.contracts import CapabilityManifest
from frankenstein.mcp_server import mcp
from frankenstein.registry import Registry


ROOT = Path(__file__).resolve().parents[1]


def test_mcp_exposes_fixed_read_and_execute_surface(tmp_path, monkeypatch):
    database = tmp_path / "registry.db"
    monkeypatch.setenv("FRANKENSTEIN_DB", str(database))
    registry = Registry(database)
    manifest = CapabilityManifest.model_validate_json(
        (ROOT / "capabilities/repo.release_normalize/1.0.0/manifest.json").read_text()
    )
    registry.register_candidate(manifest)
    registry.mark_tested(manifest.id, manifest.version)
    registry.activate(manifest.id, manifest.version)
    registry.close()

    async def exercise_server():
        async with Client(mcp, raise_exceptions=True) as client:
            tools = await client.list_tools()
            assert {tool.name for tool in tools.tools} == {
                "capability_describe",
                "capability_execute",
                "capability_list",
                "capability_search",
            }
            result = await client.call_tool(
                "capability_execute",
                {
                    "capability_id": "repo.release_normalize",
                    "arguments": {"repository": "mcp/test", "releases": []},
                },
            )
            assert not result.is_error
            assert result.structured_content["repository"] == "mcp/test"

    asyncio.run(exercise_server())
