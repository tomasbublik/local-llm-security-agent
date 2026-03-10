#!/usr/bin/env bash

# This script sets up a development shell with the virtual environment activated and environment variables loaded.
#gh commands are used in this script, so ensure you have the GitHub CLI installed and authenticated.
#and GH_TOKEN environment variable set in the .env file
set -euo pipefail

source .venv/bin/activate
set -a
source .env
set +a

echo "Using project GitHub token for:"
echo "  $GITHUB_OWNER/$GITHUB_REPO"

exec "$SHELL"
