from pathlib import Path
import re

from agent.config import settings
from agent.tools.github_advisories import get_global_advisory, find_matching_vulnerability
from agent.tools.repo_workspace import ensure_repo_cloned
from agent.tools.git_ops import (
    ensure_clean_or_reset,
    checkout_default_branch,
    create_fix_branch,
    get_git_diff,
    get_git_status,
)
from agent.tools.dependency_edit import bump_npm_dependency_version
from agent.tools.shell_guard import run_allowed_command


def is_acceptable_version(value: str | None) -> bool:
    if not value:
        return False

    lowered = value.strip().lower()
    if lowered in {"latest", "*", "x", "any", "newest"}:
        return False

    return bool(re.match(r"^[~^]?\d+(\.\d+){1,2}([\-+][A-Za-z0-9.\-]+)?$", value.strip()))

def sanitize_branch_part(value: str) -> str:
    allowed = []
    for ch in value.lower():
        if ch.isalnum() or ch in {"-", "_"}:
            allowed.append(ch)
        else:
            allowed.append("-")
    return "".join(allowed).strip("-")[:40]

def build_validation_commands(alert: dict) -> list[str]:
    ecosystem = (alert.get("ecosystem") or "").lower()

    if ecosystem == "npm":
        return [
            "npm install",
        ]

    return []

def resolve_safe_target(alert: dict) -> dict:
    patched = alert.get("first_patched_version")
    if patched:
        return {
            "mode": "dependency_bump",
            "target_dependency": alert["dependency_name"],
            "target_version": patched,
        }

    ghsa_id = alert.get("ghsa_id")
    if not ghsa_id:
        return {
            "mode": "manual_review_required",
            "reason": "Alert has no first_patched_version and no ghsa_id.",
        }

    advisory = get_global_advisory(ghsa_id)
    match = find_matching_vulnerability(
        advisory,
        ecosystem=alert["ecosystem"],
        package_name=alert["dependency_name"],
    )

    if match:
        patched = match.get("first_patched_version")
        if isinstance(patched, str) and patched.strip():
            return {
                "mode": "dependency_bump",
                "target_dependency": alert["dependency_name"],
                "target_version": patched.strip(),
            }

    return {
        "mode": "manual_review_required",
        "reason": (
            f"No patched version exists for {alert['ecosystem']} package "
            f"{alert['dependency_name']} in advisory {ghsa_id}."
        ),
    }

def build_branch_name(alert: dict) -> str:
    dep = sanitize_branch_part(alert.get("dependency_name") or "dependency")
    number = alert.get("number") or "alert"
    return f"fix/dependabot-{dep}-{number}"


def execute_dependency_fix(alert: dict, plan: dict) -> dict:
    owner = alert["repo_owner"]
    repo = alert["repo_name"]

    workdir = Path(settings.agent_workdir).expanduser().resolve()
    workdir.mkdir(parents=True, exist_ok=True)

    repo_path = ensure_repo_cloned(owner, repo, workdir)

    ensure_clean_or_reset(repo_path)
    checkout_default_branch(repo_path)

    branch_name = build_branch_name(alert)
    create_fix_branch(repo_path, branch_name)

    relevant_files = plan.get("relevant_files") or []
    commands_to_run = build_validation_commands(alert)

    changed_files = []
    package_json_path = repo_path / "package.json"

    resolution = resolve_safe_target(alert)

    if resolution["mode"] != "dependency_bump":
        return {
            "status": "manual_review_required",
            "reason": resolution["reason"],
            "alert": alert,
        }

    dependency_name = resolution["target_dependency"]
    target_version = resolution["target_version"]
    if isinstance(target_version, str):
        target_version = target_version.strip() or None

    if not is_acceptable_version(target_version):
        raise RuntimeError(
            f"Refusing to continue: invalid or missing patched version from alert: {target_version!r}"
        )

    if package_json_path.exists() and dependency_name and target_version:
        changed = bump_npm_dependency_version(package_json_path, dependency_name, target_version)
        if changed:
            changed_files.append("package.json")

    validation_ok = True
    command_outputs = []
    total_commands = len(commands_to_run)
    for index, command in enumerate(commands_to_run, start=1):
        print(f"[{index}/{total_commands}] Running validation command: {command}", flush=True)
        try:
            output = run_allowed_command(command, cwd=repo_path)
            command_outputs.append({
                "command": command,
                "output": output[-4000:],
                "ok": True,
            })
        except RuntimeError as exc:
            validation_ok = False
            command_outputs.append({
                "command": command,
                "error": str(exc),
                "ok": False,
            })

    diff = get_git_diff(repo_path)
    status = get_git_status(repo_path)

    return {
        "repo_path": str(repo_path),
        "branch_name": branch_name,
        "changed_files": changed_files,
        "git_status": status,
        "git_diff": diff,
        "command_outputs": command_outputs,
        "relevant_files": relevant_files,
        "validation_ok": validation_ok,
    }


def _extract_version_hint(text: str) -> str | None:
    tokens = text.replace(",", " ").replace(";", " ").split()
    for token in tokens:
        stripped = token.strip()
        if any(ch.isdigit() for ch in stripped) and "." in stripped:
            return stripped
    return None
