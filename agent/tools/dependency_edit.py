import json
from pathlib import Path


def _preserve_version_prefix(old_value: str, new_version: str) -> str:
    old_value = old_value.strip()
    if old_value.startswith("^"):
        return f"^{new_version}"
    if old_value.startswith("~"):
        return f"~{new_version}"
    return new_version


def bump_npm_dependency_version(package_json_path: Path, dependency_name: str, new_version: str) -> bool:
    data = json.loads(package_json_path.read_text(encoding="utf-8"))

    changed = False
    for section in ["dependencies", "devDependencies", "peerDependencies", "optionalDependencies"]:
        deps = data.get(section)
        if isinstance(deps, dict) and dependency_name in deps:
            old_value = str(deps[dependency_name])
            deps[dependency_name] = _preserve_version_prefix(old_value, new_version)
            changed = True

    if changed:
        package_json_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            )

    return changed
