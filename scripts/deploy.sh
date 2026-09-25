#!/usr/bin/env bash
# Create or update the LiteLLM gateway stack.  Usage: scripts/deploy.sh
# Needs a current login: aws login --remote --profile litellm-poc
set -euo pipefail
cd "$(dirname "$0")/.."
source env.sh
STACK="${LITELLM_STACK:-litellm-smoke}"

python scripts/make_secrets.py --prefix "$STACK"
aws cloudformation deploy \
  --stack-name "$STACK" \
  --template-file infra/litellm-smoke.yaml \
  --capabilities CAPABILITY_IAM \
  --no-fail-on-empty-changeset
aws cloudformation describe-stacks --stack-name "$STACK" \
  --query 'Stacks[0].Outputs' --output table
echo "First boot installs Docker and starts LiteLLM; allow ~3 minutes before scripts/tunnel.sh."
