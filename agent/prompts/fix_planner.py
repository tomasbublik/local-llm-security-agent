import json


def build_fix_planner_prompt(alert: dict, repo_context: dict) -> str:
    return f"""
You are a careful software maintenance agent.

Your task is to analyse a Dependabot alert and propose a safe fix plan.

Rules:
- Do not invent files that are not likely to exist.
- Prefer minimal dependency updates over broad refactors.
- Do not modify application logic unless necessary.
- If the information is insufficient, say so clearly.
- Return STRICT JSON only.
- No markdown fences.
- No explanations outside JSON.

Expected JSON schema:
{{
  "problem_summary": "string",
  "recommended_strategy": "string",
  "relevant_files": ["string"],
  "proposed_changes": [
    {{
      "file": "string",
      "change_type": "dependency_bump|code_change|config_change|unknown",
      "description": "string"
    }}
  ],
  "commands_to_run": ["string"],
  "risk_level": "low|medium|high",
  "confidence": "low|medium|high",
  "notes": "string"
}}

Dependabot alert:
{json.dumps(alert, ensure_ascii=False, indent=2)}

Repository context:
{json.dumps(repo_context, ensure_ascii=False, indent=2)}
""".strip()
