from typing import Any

from agent.tools.github_common import run_gh_api


def list_dependabot_alerts(owner: str, repo: str, state: str = "open", per_page: int = 100) -> list[dict[str, Any]]:
    path = f"/repos/{owner}/{repo}/dependabot/alerts?state={state}&per_page={per_page}"
    data = run_gh_api(path)

    if not isinstance(data, list):
        raise RuntimeError("Unexpected response format from Dependabot alerts API")

    return data


def normalize_dependabot_alert(alert: dict[str, Any], owner: str, repo: str) -> dict[str, Any]:
    dependency = alert.get("dependency") or {}
    package = dependency.get("package") or {}
    advisory = alert.get("security_advisory") or {}
    vulnerability = alert.get("security_vulnerability") or {}

    first_patched_version = None
    fpv = vulnerability.get("first_patched_version") or {}
    if isinstance(fpv, dict):
        first_patched_version = fpv.get("identifier")

    return {
        "repo_owner": owner,
        "repo_name": repo,
        "repo_full_name": f"{owner}/{repo}",
        "number": alert.get("number"),
        "state": alert.get("state"),
        "dependency_name": package.get("name"),
        "ecosystem": package.get("ecosystem"),
        "severity": advisory.get("severity") or vulnerability.get("severity"),
        "summary": advisory.get("summary") or advisory.get("description"),
        "html_url": alert.get("html_url"),
        "ghsa_id": advisory.get("ghsa_id"),
        "first_patched_version": first_patched_version,
        "vulnerable_version_range": vulnerability.get("vulnerable_version_range"),
    }

def collect_dependabot_alerts(repositories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    collected: list[dict[str, Any]] = []

    for repo in repositories:
        owner = repo["owner"]
        name = repo["name"]

        try:
            alerts = list_dependabot_alerts(owner, name, state="open", per_page=100)
        except RuntimeError as exc:
            print(f"[WARN] Could not load alerts for {owner}/{name}: {exc}")
            continue

        for alert in alerts:
            collected.append(normalize_dependabot_alert(alert, owner, name))

    return collected


def select_fix_candidate(alerts: list[dict[str, Any]]) -> dict[str, Any] | None:
    severity_rank = {
        "critical": 4,
        "high": 3,
        "moderate": 2,
        "medium": 2,
        "low": 1,
    }

    sorted_alerts = sorted(
        alerts,
        key=lambda a: (
            severity_rank.get((a.get("severity") or "").lower(), 0),
            a.get("repo_full_name") or "",
            a.get("dependency_name") or "",
        ),
        reverse=True,
    )

    return sorted_alerts[0] if sorted_alerts else None
