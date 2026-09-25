# Source this before any AWS or gateway command:  source env.sh
#
# Points the AWS CLI and boto3 at the project's own profile and clears the
# JupyterHub's built-in AWS role, which would otherwise be picked up first and
# send commands to the hub's account instead of yours.

# AWS_BEARER_TOKEN_BEDROCK is a Bedrock API key; when set, the AWS CLI and boto3
# use it for Bedrock calls instead of the profile, i.e. possibly another account.
unset AWS_ROLE_ARN AWS_WEB_IDENTITY_TOKEN_FILE AWS_ROLE_SESSION_NAME \
      AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN \
      AWS_BEARER_TOKEN_BEDROCK

# greenfield is the account the gateway is built in. It is reached by
# assuming a role from the litellm-poc login (see README), so `aws login`
# always targets litellm-poc.
export AWS_PROFILE="${LITELLM_AWS_PROFILE:-greenfield}"
export AWS_REGION="${LITELLM_AWS_REGION:-us-east-2}"
export AWS_DEFAULT_REGION="$AWS_REGION"

# AWS CLI v2 and session-manager-plugin are installed in ~/.local/bin (see README).
case ":$PATH:" in *":$HOME/.local/bin:"*) ;; *) export PATH="$HOME/.local/bin:$PATH" ;; esac

_here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$_here/.venv/bin/activate" ]; then
  . "$_here/.venv/bin/activate"
else
  echo "env.sh: no .venv yet — create it with the commands in the README" >&2
fi
unset _here
