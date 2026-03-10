# local-llm-security-agent

Minimal PoC of an agent that locally selects an open Dependabot alert from GitHub, asks a local LLM to propose a fix plan, and then performs a constrained dependency fix in the repository.

At the moment, the flow is aimed mainly at `npm` projects:
- fetches Dependabot alerts via `gh`
- selects one candidate to fix
- sends repository context to a local model via `ollama`
- updates the dependency version in `package.json`
- runs a constrained validation command set, for example `npm install`

## Required tools

- `python3`
- `git`
- `gh` (GitHub CLI)
- `ollama`

For target repositories, you also need the tools that the agent may run during validation, typically:
- `npm`
- optionally `pnpm`, `yarn`, or `pytest` if you extend the allowed command list

## Quick start

```bash
bash scripts/setup.sh
cp .env.example .env
bash scripts/run.sh
```

You can also run it directly:

```bash
source .venv/bin/activate
python -m agent.main
```

## Installation step by step

### 1. Create the virtual environment

```bash
bash scripts/setup.sh
```

The script:
- creates `.venv`
- installs dependencies from `requirements.txt`

### 2. Configure `.env`

```bash
cp .env.example .env
```

Then update the values to match the repositories you want to scan and the local model you want to use.

### 3. Authenticate GitHub CLI

The agent uses `gh api`, so GitHub CLI authentication must be working. One of these approaches is sufficient:

```bash
gh auth login
```

or export a token into your environment if that is how you normally use `gh`.

### 4. Verify Ollama

The local Ollama service must be running, and the model configured in `OLLAMA_MODEL` must be available.

Example:

```bash
ollama list
ollama run qwen2.5-coder:14b "say hi"
```

## Configuration via `.env`

The example configuration is in [`.env.example`](/Users/tomasbublik/workspace/mine/local-llm-security-agent-poc/.env.example).

### LLM and logging

- `OLLAMA_MODEL`
  Local model used for planning the fix.
  Example: `qwen2.5-coder:14b`

- `OLLAMA_HOST`
  Address of the Ollama service.
  In the current code this is printed in logs, but the model invocation itself uses the `ollama run` CLI.

- `LOG_LEVEL`
  Currently informational only and printed on start-up.

### Target repository selection

- `TARGET_SCOPE`
  Supported values:
  - `single_repo`
  - `owner_all_repos`

- `TARGET_OWNER`
  GitHub owner whose repository or repositories should be scanned.

- `TARGET_REPO`
  Repository name. Required when `TARGET_SCOPE=single_repo`.

### Local agent workspace

- `AGENT_WORKDIR`
  Directory where the agent clones repositories and reuses them between runs.
  Example: `/tmp/llm-security-agent`

### GitHub mode and future behaviour

- `GITHUB_MODE`
  Currently loaded from configuration, but it does not yet drive any meaningful branching logic in the PoC.

- `AUTO_PUSH`
  Currently loaded, but not yet used.

- `AUTO_CREATE_PR`
  Currently loaded, but not yet used.

### Note on `GITHUB_OWNER`, `GITHUB_REPO`, and `GH_TOKEN`

[`.env.example`](/Users/tomasbublik/workspace/mine/local-llm-security-agent-poc/.env.example) also contains `GITHUB_OWNER` and `GITHUB_REPO`. These are used mainly by the helper script [`scripts/dev-shell.sh`](/Users/tomasbublik/workspace/mine/local-llm-security-agent-poc/scripts/dev-shell.sh), not by the main agent run.

`scripts/dev-shell.sh` also expects `GH_TOKEN` in `.env`, even though that variable is not currently present in `.env.example`. For the main agent flow, the important requirement is simply that `gh auth` works.

## Recommended `.env` setup

### Single repository

```dotenv
OLLAMA_MODEL=qwen2.5-coder:14b
OLLAMA_HOST=http://localhost:11434
LOG_LEVEL=INFO

TARGET_SCOPE=single_repo
TARGET_OWNER=your-github-login
TARGET_REPO=your-repo-name

AGENT_WORKDIR=/tmp/llm-security-agent

GITHUB_MODE=pr_only
AUTO_PUSH=false
AUTO_CREATE_PR=false
```

### All repositories for one owner

```dotenv
OLLAMA_MODEL=qwen2.5-coder:14b
OLLAMA_HOST=http://localhost:11434
LOG_LEVEL=INFO

TARGET_SCOPE=owner_all_repos
TARGET_OWNER=your-github-login
TARGET_REPO=

AGENT_WORKDIR=/tmp/llm-security-agent

GITHUB_MODE=pr_only
AUTO_PUSH=false
AUTO_CREATE_PR=false
```

## How it works

After running:

```bash
bash scripts/run.sh
```

the agent performs this flow:

1. prints the active configuration
2. resolves the target repositories
3. fetches open Dependabot alerts
4. selects one candidate based on severity
5. generates a fix plan via the local LLM
6. clones or refreshes the repository in `AGENT_WORKDIR`
7. creates a fix branch
8. updates `package.json` to the first patched version from the alert
9. runs validation commands
10. prints `git diff`, `git status`, and execution metadata

## What you will see during execution

During validation, the agent now prints command progress as well, for example:

```text
Executing bounded dependency fix...

[1/1] Running validation command: npm install
[exec] Starting: npm install
[exec] Working directory: /tmp/llm-security-agent/owner__repo
...
[exec] Finished with exit code 0: npm install
```

This is useful when `npm install` or another allowed command takes longer to complete.

## Development shell

If you want a shell with the virtual environment activated and `.env` loaded, you can use:

```bash
bash scripts/dev-shell.sh
```

This script:
- activates `.venv`
- loads variables from `.env`
- opens a new shell

## Current PoC limitations

- it mainly fixes `npm` dependencies in `package.json`
- validation commands are allow-listed in [`agent/tools/shell_guard.py`](/Users/tomasbublik/workspace/mine/local-llm-security-agent-poc/agent/tools/shell_guard.py)
- repository preparation uses `git reset --hard` and `git clean -fd` on the working clone inside `AGENT_WORKDIR`
- the branch is created locally, but push/PR flow is not yet finished
- `OLLAMA_HOST`, `GITHUB_MODE`, `AUTO_PUSH`, and `AUTO_CREATE_PR` are only partially used at present

## Useful commands

```bash
# installation
bash scripts/setup.sh

# normal run
bash scripts/run.sh

# direct run without the wrapper
source .venv/bin/activate
python -m agent.main

# development shell
bash scripts/dev-shell.sh
```
