#!/usr/bin/env bash
# Forward localhost:4000 on this machine to LiteLLM on the gateway instance,
# through SSM Session Manager (no open ports). Runs until Ctrl-C, so start it
# in its own terminal.  Usage: scripts/tunnel.sh
set -euo pipefail
cd "$(dirname "$0")/.."
source env.sh
STACK="${LITELLM_STACK:-litellm-smoke}"
PORT="${LITELLM_LOCAL_PORT:-4000}"

ID=$(aws cloudformation describe-stacks --stack-name "$STACK" \
  --query "Stacks[0].Outputs[?OutputKey=='InstanceId'].OutputValue" --output text)
echo "Tunnel: localhost:$PORT -> $ID:4000 (Ctrl-C to close)"
exec aws ssm start-session --target "$ID" \
  --document-name AWS-StartPortForwardingSession \
  --parameters "{\"portNumber\":[\"4000\"],\"localPortNumber\":[\"$PORT\"]}"
