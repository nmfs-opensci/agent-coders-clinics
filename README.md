# agent-coders-clinics
Repo for the agent-coders team in Openscapes Champions cohort 2026

## LiteLLM gateway (work in progress)

A test of running Claude Code through a LiteLLM proxy to Amazon Bedrock, with a
separate budget and expiry for each participant's key. See issue #1.

### Environment setup (JupyterHub, Linux x86_64)

AWS CLI v2 and the Session Manager plugin are not pip packages. Install them
into `~/.local`:

```bash
curl -sSfL https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o awscliv2.zip
unzip -q awscliv2.zip && ./aws/install -i ~/.local/aws-cli -b ~/.local/bin --update

curl -sSfL https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_64bit/session-manager-plugin.deb -o smp.deb
dpkg-deb -x smp.deb smp && mkdir -p ~/.local/sessionmanagerplugin
cp -r smp/usr/local/sessionmanagerplugin/* ~/.local/sessionmanagerplugin/
ln -sf ~/.local/sessionmanagerplugin/bin/session-manager-plugin ~/.local/bin/session-manager-plugin
```

Then build the Python environment and sign in to AWS:

```bash
/srv/conda/bin/python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
source env.sh                               # run in every new terminal
aws login --remote --profile litellm-poc    # short-lived credentials; sign in to the org's management account
```

The gateway is built in a separate member account, `litellm-smoke-test`,
created from the organization's management account. The `litellm-smoke`
profile reaches it by assuming that account's `OrganizationAccountAccessRole`
with the `litellm-poc` login. Set it up once (replace the account ID):

```bash
aws configure set role_arn arn:aws:iam::<ACCOUNT_ID>:role/OrganizationAccountAccessRole --profile litellm-smoke
aws configure set source_profile litellm-poc --profile litellm-smoke
aws configure set region us-east-2 --profile litellm-smoke
```

`env.sh` clears the JupyterHub's own AWS role and selects the `litellm-smoke`
profile in `us-east-2`. Set `LITELLM_AWS_PROFILE` or `LITELLM_AWS_REGION`
before sourcing it to use a different profile or Region. Always name the
profile in `aws login`, since the default profile is the role, not the login.

## Reuse and citation

This work is released under [CC0 1.0 Universal](LICENSE) and is free of known
copyright restrictions. You are free to use, copy, modify, and redistribute it for
any purpose, including commercially. Attribution is appreciated but not required —
you do not need to cite the authors or ask permission.
