#!/usr/bin/env bash
# Delete everything the gateway created: the CloudFormation stack (network,
# instance, disk, role) and its secrets in Parameter Store. Keys, budgets and
# spend history on the instance disk are lost.  Usage: scripts/teardown.sh
set -euo pipefail
cd "$(dirname "$0")/.."
source env.sh
STACK="${LITELLM_STACK:-litellm-smoke}"

read -r -p "Delete stack '$STACK' and /$STACK/* secrets in $AWS_REGION? Type the stack name: " answer
[ "$answer" = "$STACK" ] || { echo "Cancelled."; exit 1; }

aws cloudformation delete-stack --stack-name "$STACK"
aws cloudformation wait stack-delete-complete --stack-name "$STACK"
echo "Stack deleted."
for name in master-key db-password salt-key; do
  aws ssm delete-parameter --name "/$STACK/$name" 2>/dev/null && echo "Deleted /$STACK/$name" || true
done
rm -f secrets/*.key
echo "Teardown complete."
