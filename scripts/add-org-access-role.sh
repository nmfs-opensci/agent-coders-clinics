#!/usr/bin/env bash
# Run inside a member account (e.g. in CloudShell) that lacks the role
# Organizations normally creates. Lets the management account assume
# OrganizationAccountAccessRole here with admin rights.
set -euo pipefail
MGMT=$(aws organizations describe-organization \
  --query Organization.MasterAccountId --output text)
echo "Management account: $MGMT"

cat > /tmp/trust.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"AWS": "arn:aws:iam::${MGMT}:root"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

aws iam create-role --role-name OrganizationAccountAccessRole \
  --assume-role-policy-document file:///tmp/trust.json \
  --query Role.Arn --output text
aws iam attach-role-policy --role-name OrganizationAccountAccessRole \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
echo "Done: OrganizationAccountAccessRole created."
