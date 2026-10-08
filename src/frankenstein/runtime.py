from __future__ import annotations

from typing import Any, Callable

from .registry import Registry
from .issue_risk import run as issue_risk
from .release_normalize import run as release_normalize
from .release_readiness import run as release_readiness


ENTRYPOINTS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "frankenstein.release_normalize:run": release_normalize,
    "frankenstein.issue_risk:run": issue_risk,
}
WORKFLOWS = {"frankenstein.release_readiness:run": release_readiness}


def execute(registry: Registry, capability_id: str, raw_input: dict[str, Any]) -> dict[str, Any]:
    return _execute(registry, capability_id, raw_input, set())


def _execute(
    registry: Registry, capability_id: str, raw_input: dict[str, Any], path: set[str]
) -> dict[str, Any]:
    if capability_id in path:
        raise ValueError(f"capability dependency cycle detected at {capability_id}")
    record = registry.get(capability_id)
    manifest = record["manifest"]
    if any(manifest["permissions"].values()):
        raise PermissionError("capability requests authority not granted by this runtime")
    properties = manifest["input_schema"].get("properties", {})
    projected_input = {key: raw_input[key] for key in properties if key in raw_input}
    dependencies = {}
    for reference in manifest["requires"]:
        dependency_id, _, required_version = reference.partition("@")
        dependency = registry.get(dependency_id)
        if dependency["version"] != required_version:
            raise ValueError(f"active dependency does not match {reference}")
        dependencies[dependency_id] = _execute(
            registry, dependency_id, raw_input, path | {capability_id}
        )
    if manifest["kind"] == "workflow":
        try:
            workflow = WORKFLOWS[manifest["entrypoint"]]
        except KeyError as error:
            raise PermissionError("entrypoint is not approved by this runtime") from error
        return workflow(projected_input, dependencies)
    try:
        entrypoint = ENTRYPOINTS[manifest["entrypoint"]]
    except KeyError as error:
        raise PermissionError("entrypoint is not approved by this runtime") from error
    return entrypoint(projected_input)
