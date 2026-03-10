from pathlib import Path
from typing import Iterable


MANIFEST_CANDIDATES = [
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "requirements.txt",
    "pyproject.toml",
    "poetry.lock",
    "Pipfile",
    "Pipfile.lock",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "go.mod",
    "Cargo.toml",
    "Gemfile",
    "Gemfile.lock",
]


def safe_read_text(path: Path, max_chars: int = 20000) -> str:
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = path.read_text(encoding="utf-8", errors="ignore")
    return content[:max_chars]


def list_root_files(repo_path: Path) -> list[str]:
    items = []
    for child in sorted(repo_path.iterdir(), key=lambda p: p.name.lower()):
        if child.name.startswith(".git"):
            continue
        items.append(child.name + ("/" if child.is_dir() else ""))
    return items


def find_manifest_files(repo_path: Path) -> list[Path]:
    found: list[Path] = []
    for name in MANIFEST_CANDIDATES:
        p = repo_path / name
        if p.exists() and p.is_file():
            found.append(p)
    return found


def collect_repo_context(repo_path: Path) -> dict:
    root_files = list_root_files(repo_path)
    manifests = find_manifest_files(repo_path)

    manifest_contents = []
    for manifest in manifests:
        manifest_contents.append({
            "path": str(manifest.relative_to(repo_path)),
            "content": safe_read_text(manifest),
        })

    readme = None
    for candidate in ["README.md", "readme.md", "README.txt"]:
        p = repo_path / candidate
        if p.exists() and p.is_file():
            readme = {
                "path": str(p.relative_to(repo_path)),
                "content": safe_read_text(p, max_chars=12000),
            }
            break

    return {
        "root_files": root_files,
        "manifest_files": manifest_contents,
        "readme": readme,
    }
