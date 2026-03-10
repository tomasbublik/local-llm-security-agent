import subprocess
from pathlib import Path


def ensure_repo_cloned(owner: str, repo: str, workdir: Path) -> Path:
    repo_dir = workdir / f"{owner}__{repo}"

    if repo_dir.exists():
        subprocess.run(
            ["git", "-C", str(repo_dir), "pull"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return repo_dir

    clone_url = f"https://github.com/{owner}/{repo}.git"

    # Why "--depth", "1"? Faster, no need for history, lower disk space
    result = subprocess.run(
        ["git", "clone", "--depth", "1", clone_url, str(repo_dir)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    return repo_dir
