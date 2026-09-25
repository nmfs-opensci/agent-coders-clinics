#!/usr/bin/env bash
# Start Claude Code through the LiteLLM gateway as one test user.
# Usage: scripts/claude-gateway.sh USER [claude arguments...]
# Needs a key made with scripts/keys.py create USER. Uses the stack's HTTPS
# address unless LITELLM_URL is set (e.g. http://localhost:4000 via scripts/tunnel.sh).
set -euo pipefail
user="${1:?usage: scripts/claude-gateway.sh USER [claude args]}"
shift
keyfile="$(cd "$(dirname "$0")/.." && pwd)/secrets/$user.key"
[ -r "$keyfile" ] || { echo "No key for $user: run python scripts/keys.py create $user" >&2; exit 1; }

# Settings inherited from other Claude launchers would bypass the gateway.
unset CLAUDE_CODE_USE_BEDROCK CLAUDE_CODE_USE_VERTEX ANTHROPIC_API_KEY \
      AWS_BEARER_TOKEN_BEDROCK ANTHROPIC_MODEL ANTHROPIC_SMALL_FAST_MODEL

if [ -z "${LITELLM_URL:-}" ]; then
  cd "$(dirname "$0")/.." && source env.sh
  LITELLM_URL=$(aws cloudformation describe-stacks --stack-name "${LITELLM_STACK:-litellm-smoke}" \
    --query "Stacks[0].Outputs[?OutputKey=='GatewayUrl'].OutputValue" --output text)
fi
export ANTHROPIC_BASE_URL="$LITELLM_URL"
ANTHROPIC_AUTH_TOKEN="$(tr -d '[:space:]' < "$keyfile")"
export ANTHROPIC_AUTH_TOKEN
# Claude Code picks models by tier; map every tier to a model the gateway serves.
export ANTHROPIC_MODEL=claude-sonnet-4-6
export ANTHROPIC_DEFAULT_OPUS_MODEL=claude-opus-4-6
export ANTHROPIC_DEFAULT_SONNET_MODEL=claude-sonnet-4-6
export ANTHROPIC_DEFAULT_HAIKU_MODEL=claude-haiku-4-5-20251001
exec claude "$@"
