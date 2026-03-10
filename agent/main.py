from pprint import pprint

from agent.config import settings
from agent.tools.github_repos import resolve_target_repositories
from agent.tools.github_alerts import collect_dependabot_alerts, select_fix_candidate
from agent.agent_loop import plan_fix_for_alert

def main() -> None:
    print(f"OLLAMA_MODEL={settings.ollama_model}")
    print(f"OLLAMA_HOST={settings.ollama_host}")
    print(f"LOG_LEVEL={settings.log_level}")

    print("Local LLM Security Agent PoC")
    print(f"TARGET_SCOPE={settings.target_scope}")
    print(f"TARGET_OWNER={settings.target_owner}")
    print(f"TARGET_REPO={settings.target_repo}")

    repositories = resolve_target_repositories(
        target_scope=settings.target_scope,
        target_owner=settings.target_owner,
        target_repo=settings.target_repo,
    )

    print(f"Resolved repositories: {len(repositories)}")
    for repo in repositories:
        print(f" - {repo['full_name']}")

    alerts = collect_dependabot_alerts(repositories)
    print(f"Collected open Dependabot alerts: {len(alerts)}")

    candidate = select_fix_candidate(alerts)
    print("Selected candidate:")
    pprint(candidate)

    if candidate:
        print("\nGenerating fix plan...\n")
        result = plan_fix_for_alert(candidate)
        pprint(result)
    else:
        print("No candidate alert found.")



if __name__ == "__main__":
    main()
