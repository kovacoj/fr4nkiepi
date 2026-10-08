from __future__ import annotations

from typing import Any

from mcp.server import MCPServer

from .cli import _database_path
from .registry import Registry
from .runtime import execute


mcp = MCPServer(
    "frankenstein-control-plane",
    instructions="Search and describe active capabilities before executing one.",
)


def _with_registry(function):
    registry = Registry(_database_path())
    try:
        return function(registry)
    finally:
        registry.close()


@mcp.tool()
def capability_search(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    """Search active, verified capabilities by ID or description."""
    if not 1 <= max_results <= 20:
        raise ValueError("max_results must be between 1 and 20")
    return _with_registry(lambda registry: registry.search(query)[:max_results])


@mcp.tool()
def capability_describe(capability_id: str) -> dict[str, Any]:
    """Describe the active version, contract, dependencies, and permissions."""
    return _with_registry(lambda registry: registry.get(capability_id))


@mcp.tool()
def capability_execute(capability_id: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute an active capability under server-owned permission policy."""
    return _with_registry(lambda registry: execute(registry, capability_id, arguments))


@mcp.tool()
def capability_list() -> list[dict[str, Any]]:
    """List active capability versions."""
    return _with_registry(lambda registry: registry.list("active"))


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
