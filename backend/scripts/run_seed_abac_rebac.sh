#!/bin/bash
# Deprecated wrapper: use the unified seed_all_templates.py instead.

cd "$(dirname "$0")/.."

echo "This script is deprecated. Running unified template seeder instead..."

python scripts/seed_all_templates.py
