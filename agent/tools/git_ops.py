import subprocess
from pathlib import Path


def run_git(args: list[str], cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())

    return result.stdout.strip()


def ensure_clean_or_reset(repo_path: Path) -> None:
    run_git(["reset", "--hard"], cwd=repo_path)
    run_git(["clean", "-fd"], cwd=repo_path)


def get_default_branch(repo_path: Path) -> str:
    """
    Detect the default branch of the repository.
    Tries to get it from 'origin' remote symbol-ref.
    """
    try:
        # This usually returns "ref: refs/heads/main\t"
        output = run_git(["symbol-ref", "refs/remotes/origin/HEAD"], cwd=repo_path)
        return output.strip().split("/")[-1]
    except RuntimeError:
        # Fallback to a common list or trying to see what we have
        for branch in ["main", "master", "develop"]:
            try:
                run_git(["rev-parse", "--verify", branch], cwd=repo_path)
                return branch
            except RuntimeError:
                continue

    # Final fallback: current branch
    return run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_path)


def checkout_default_branch(repo_path: Path, default_branch: str | None = None) -> None:
    if default_branch is None:
        default_branch = get_default_branch(repo_path)
    run_git(["checkout", default_branch], cwd=repo_path)
    run_git(["pull", "--ff-only"], cwd=repo_path)


def create_fix_branch(repo_path: Path, branch_name: str) -> None:
    run_git(["checkout", "-B", branch_name], cwd=repo_path)


def get_git_diff(repo_path: Path) -> str:
    return run_git(["diff", "--", "."], cwd=repo_path)


def get_git_status(repo_path: Path) -> str:
    return run_git(["status", "--short"], cwd=repo_path)


def stage_all(repo_path: Path) -> None:
    run_git(["add", "."], cwd=repo_path)


def commit(repo_path: Path, message: str) -> None:
    run_git(["commit", "-m", message], cwd=repo_path)


def push_branch(repo_path: Path, branch_name: str) -> None:
    run_git(["push", "-u", "origin", branch_name], cwd=repo_path)
