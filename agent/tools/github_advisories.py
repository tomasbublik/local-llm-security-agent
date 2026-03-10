from typing import Any

from agent.tools.github_common import run_gh_api


def get_global_advisory(ghsa_id: str) -> dict[str, Any]:
    data = run_gh_api(f"/advisories/{ghsa_id}")
    if not isinstance(data, dict):
        raise RuntimeError("Unexpected response format from advisory API")
    return data


def find_matching_vulnerability(advisory: dict[str, Any], ecosystem: str, package_name: str) -> dict[str, Any] | None:
    vulnerabilities = advisory.get("vulnerabilities") or []
    for item in vulnerabilities:
        package = item.get("package") or {}
        if (
                (package.get("ecosystem") or "").lower() == ecosystem.lower()
                and package.get("name") == package_name
        ):
            return item
    return None
