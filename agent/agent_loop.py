import json
from pathlib import Path

from agent.config import settings
from agent.tools.repo_context import collect_repo_context
from agent.tools.ollama_client import generate_with_ollama
from agent.prompts.fix_planner import build_fix_planner_prompt
from agent.tools.repo_workspace import ensure_repo_cloned


def plan_fix_for_alert(alert: dict) -> dict:
    if not settings.agent_workdir:
        raise RuntimeError("AGENT_WORKDIR is not set")

    workdir = Path(settings.agent_workdir).expanduser().resolve()
    workdir.mkdir(parents=True, exist_ok=True)

    owner = alert["repo_owner"]
    repo = alert["repo_name"]

    repo_path = ensure_repo_cloned(owner, repo, workdir)

    if not repo_path.exists() or not repo_path.is_dir():
        raise RuntimeError(f"AGENT_WORKDIR does not exist or is not a directory: {repo_path}")

    repo_context = collect_repo_context(repo_path)
    prompt = build_fix_planner_prompt(alert, repo_context)
    raw_response = generate_with_ollama(settings.ollama_model, prompt)

    try:
        parsed = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Model did not return valid JSON.\n"
            f"Raw response:\n{raw_response}"
        ) from exc

    return {
        "alert": alert,
        "repo_context_summary": {
            "root_file_count": len(repo_context["root_files"]),
            "manifest_file_count": len(repo_context["manifest_files"]),
            "has_readme": repo_context["readme"] is not None,
        },
        "plan": parsed,
    }
