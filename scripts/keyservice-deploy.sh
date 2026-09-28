#!/usr/bin/env bash
# Install or update the workshop key service on the running gateway, over SSM.
# Usage: scripts/keyservice-deploy.sh   (also after a rebuild, once LiteLLM is up)
# Copies keyservice/keyservice.py to the instance, (re)starts its container on
# the litellm network, and points Caddy's /workshop/* at it. The master key is
# copied from litellm.env on the instance; it never passes through this machine.
# Sign-up stays closed until scripts/workshop.py open.
set -euo pipefail
cd "$(dirname "$0")/.."
source env.sh
STACK="${LITELLM_STACK:-litellm-smoke}"
# 3.13-alpine, pinned by digest (multi-arch; includes arm64).
IMAGE=public.ecr.aws/docker/library/python:3.13-alpine@sha256:79e7a9b9ff1cbceff819f856fb374477792a5967759d94df266de7b7b4120e6f

ID=$(aws cloudformation describe-stacks --stack-name "$STACK" \
  --query "Stacks[0].Outputs[?OutputKey=='InstanceId'].OutputValue" --output text)
CODE_B64=$(base64 -w0 keyservice/keyservice.py)

REMOTE=$(cat <<EOF
set -euo pipefail
cd /opt/litellm
mkdir -p keyservice/state
echo $CODE_B64 | base64 -d > keyservice/keyservice.py
umask 077
grep '^LITELLM_MASTER_KEY=' litellm.env > keyservice.env
umask 022
docker rm -f keyservice >/dev/null 2>&1 || true
docker run -d --name keyservice --restart unless-stopped --network litellm \\
  --env-file keyservice.env \\
  -v /opt/litellm/keyservice/keyservice.py:/app/keyservice.py:ro \\
  -v /opt/litellm/keyservice/state:/state \\
  $IMAGE python /app/keyservice.py >/dev/null
# Rewrite the Caddyfile in place (same file, so the container's mount sees it).
HOST=\$(head -1 Caddyfile | cut -d' ' -f1)
printf '%s {\n\thandle /workshop/* {\n\t\treverse_proxy keyservice:8080\n\t}\n\thandle {\n\t\treverse_proxy litellm:4000\n\t}\n}\n' "\$HOST" > Caddyfile
docker exec caddy caddy reload --config /etc/caddy/Caddyfile
sleep 3
curl -fsS "https://\$HOST/workshop/health" && echo " keyservice: up at https://\$HOST/workshop/"
EOF
)

CMD_ID=$(aws ssm send-command --instance-ids "$ID" --document-name AWS-RunShellScript \
  --comment "keyservice deploy" \
  --parameters "commands=[\"echo $(printf '%s' "$REMOTE" | base64 -w0) | base64 -d | bash\"]" \
  --query Command.CommandId --output text)
aws ssm wait command-executed --command-id "$CMD_ID" --instance-id "$ID" || true
aws ssm get-command-invocation --command-id "$CMD_ID" --instance-id "$ID" \
  --query '[Status,StandardOutputContent,StandardErrorContent]' --output text
