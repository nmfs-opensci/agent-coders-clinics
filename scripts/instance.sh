#!/usr/bin/env bash
# Stop, start, or show the gateway instance.  Usage: scripts/instance.sh stop|start|status
# Stopped, it costs only its disk (~$1.60/month); the public IPv4 is released.
# Keys, budgets and spend live on the disk and survive a stop.
set -euo pipefail
cd "$(dirname "$0")/.."
source env.sh
STACK="${LITELLM_STACK:-litellm-smoke}"

ID=$(aws cloudformation describe-stacks --stack-name "$STACK" \
  --query "Stacks[0].Outputs[?OutputKey=='InstanceId'].OutputValue" --output text)
case "${1:-status}" in
  stop)   aws ec2 stop-instances --instance-ids "$ID" --output text >/dev/null
          aws ec2 wait instance-stopped --instance-ids "$ID" ;;
  start)  aws ec2 start-instances --instance-ids "$ID" --output text >/dev/null
          aws ec2 wait instance-running --instance-ids "$ID" ;;
  status) ;;
  *) echo "usage: $0 stop|start|status" >&2; exit 2 ;;
esac
aws ec2 describe-instances --instance-ids "$ID" \
  --query 'Reservations[0].Instances[0].[InstanceId,State.Name,InstanceType]' --output text
