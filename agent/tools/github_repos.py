from typing import Any

from agent.tools.github_common import run_gh_api


def list_user_repositories(owner: str, per_page: int = 100) -> list[dict[str, Any]]:
    # For personal repos under the authenticated user's account.
    path = f"/user/repos?affiliation=owner&per_page={per_page}&sort=full_name"
    repos = run_gh_api(path)

    if not isinstance(repos, list):
        raise RuntimeError("Unexpected response format from /user/repos")

    filtered = [
        repo for repo in repos
        if isinstance(repo, dict)
           and (repo.get("owner") or {}).get("login") == owner
    ]
    return filtered


def normalize_repository(repo: dict[str, Any]) -> dict[str, Any]:
    owner = (repo.get("owner") or {}).get("login", "")
    name = repo.get("name", "")
    return {
        "owner": owner,
        "name": name,
        "full_name": repo.get("full_name", f"{owner}/{name}"),
        "private": repo.get("private", False),
        "default_branch": repo.get("default_branch"),
    }


def resolve_target_repositories(target_scope: str, target_owner: str, target_repo: str) -> list[dict[str, Any]]:
    if target_scope == "single_repo":
        if not target_owner or not target_repo:
            raise RuntimeError("TARGET_OWNER and TARGET_REPO must be set for single_repo scope")

        return [{
            "owner": target_owner,
            "name": target_repo,
            "full_name": f"{target_owner}/{target_repo}",
            "private": None,
            "default_branch": None,
        }]

    if target_scope == "owner_all_repos":
        repos = list_user_repositories(target_owner)
        return [normalize_repository(r) for r in repos]

    raise RuntimeError(f"Unsupported TARGET_SCOPE: {target_scope}")
