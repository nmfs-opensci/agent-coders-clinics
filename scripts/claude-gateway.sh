#!/usr/bin/env bash
# Start Claude Code through the LiteLLM gateway as one test user.
# Usage: scripts/claude-gateway.sh USER [claude arguments...]
# Needs scripts/tunnel.sh running and a key made with scripts/keys.py create USER.
set -euo pipefail
user="${1:?usage: scripts/claude-gateway.sh USER [claude args]}"
shift
keyfile="$(cd "$(dirname "$0")/.." && pwd)/secrets/$user.key"
[ -r "$keyfile" ] || { echo "No key for $user: run python scripts/keys.py create $user" >&2; exit 1; }

# Settings inherited from other Claude launchers would bypass the gateway.
unset CLAUDE_CODE_USE_BEDROCK CLAUDE_CODE_USE_VERTEX ANTHROPIC_API_KEY \
      AWS_BEARER_TOKEN_BEDROCK ANTHROPIC_MODEL ANTHROPIC_SMALL_FAST_MODEL

export ANTHROPIC_BASE_URL="${LITELLM_URL:-http://localhost:4000}"
ANTHROPIC_AUTH_TOKEN="$(tr -d '[:space:]' < "$keyfile")"
export ANTHROPIC_AUTH_TOKEN
# Claude Code picks models by tier; map every tier to an alias the gateway serves.
export ANTHROPIC_MODEL=sonnet
export ANTHROPIC_DEFAULT_OPUS_MODEL=sonnet
export ANTHROPIC_DEFAULT_SONNET_MODEL=sonnet
export ANTHROPIC_DEFAULT_HAIKU_MODEL=haiku
exec claude "$@"
