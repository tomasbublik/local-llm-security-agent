#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt

echo "Setup complete."
echo "Next:"
echo "  cp .env.example .env"
echo "  source .venv/bin/activate"
echo "  python -m agent.main"
