# LiteLLM gateway for Claude Code (issue #1)

Goal: a workshop of ~20 people runs Claude Code through
**Claude Code → LiteLLM proxy → Amazon Bedrock**, each person holding a
temporary LiteLLM virtual key with its own budget and expiry, while the only AWS
access is a role on the server. First a one-user smoke test, then hand over to
an org account.

Why not the ESIP 2026 pattern (Rich's `OpenScienceComputing/ESIP-2026-virtual-agent`):
there everyone shares one IAM access key, so Bedrock cannot tell participants
apart and there is no per-person spending cap.

## Decisions and why

- **Smoke test in Eli's personal AWS account, then hand over to an org account**
  (not NOAA; likely ESIP, possibly Openscapes). So nothing may be tied to one
  account: account, Region, and model are parameters; the AWS profile name is a
  setting (`LITELLM_AWS_PROFILE`, default `litellm-poc`).
- **Region us-west-2.** One of the two Regions with the fullest Claude-on-Bedrock
  coverage; `us.` inference profiles route across US Regions anyway; latency is
  dominated by the model. Change it with `LITELLM_AWS_REGION` if the org already
  works elsewhere.
- **Credentials via `aws login`** (AWS CLI v2 ≥ 2.32), short-lived, into the
  profile `litellm-poc`. No long-lived access keys anywhere.
- **Claude Code for the smoke test runs on the JupyterHub**, so the SSM tunnel
  and `session-manager-plugin` live here, not on a laptop.
- **Proposed one-user deployment** (not yet approved or built): one EC2
  `t4g.small` running LiteLLM + Postgres 16 in Docker Compose; instance role
  allowed to invoke one inference profile; LiteLLM master key and DB password in
  SSM Parameter Store (SecureString); reach it through SSM port forwarding to
  `localhost:4000`; everything from one CloudFormation stack so teardown is one
  command. Rough cost ≈ $17/month if left running (instance ~$12, public IPv4
  ~$3.60, 20 GB gp3 ~$1.60); Bedrock tokens per use. EBS and the IPv4 address
  charge even while the instance is stopped.
- **Rejected for the smoke test:** ECS Fargate + RDS + ALB — sturdier but ~$50–80/month
  idle. Revisit for the workshop only if the single instance proves inadequate.
- **Workshop open question:** participants have no AWS logins, so the SSM tunnel
  will not work for them; they need an HTTPS endpoint — Caddy on the instance
  (needs a domain name) or an ALB + ACM certificate (~$16/month more). Eli to decide.

## Environment (pared down on purpose)

The hub's default Python env is a large geospatial image, which hides missing
dependencies. This work uses only:

- `.venv` built from `requirements.txt` with `/srv/conda/bin/python3.12 -m venv .venv`.
  `boto3[crt]` — the `crt` extra is **required** for boto3 to read `aws login`
  credentials (botocore raises an error without it).
- AWS CLI v2 and `session-manager-plugin` installed into `~/.local` (not pip —
  PyPI `awscli` is v1 and has no `aws login`). Install commands are in the README.
- `source env.sh` before every AWS command. It **unsets the hub's own role**
  (`AWS_ROLE_ARN` + web identity token, account `…2472`, role
  `nmfs-openscapes-prod`), which the AWS SDKs would otherwise use first. In Claude
  Code each Bash call is a fresh shell, so prefix commands with `source env.sh &&`.
- `~/.aws/config` `[default]` is managed by the ESIP-2026 setup script (a
  long-lived `bedrock-class` IAM user in account `…0392`). Leave it alone; use the
  `litellm-poc` profile. That `…0392` account may be ESIP's — relevant if ESIP
  becomes the org target.

## Gotchas to remember

- Claude Code → gateway: `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN` (LiteLLM key),
  `ANTHROPIC_MODEL`, and `ANTHROPIC_DEFAULT_HAIKU_MODEL` set to an alias the gateway
  knows — Claude Code's background calls use the small model and fail otherwise.
  `CLAUDE_CODE_USE_BEDROCK` must be unset (Eli's `claude-bedrock` function sets it).
- LiteLLM checks the budget before a request, so one request can overshoot a
  small budget slightly.
- A new personal account may start with low Bedrock tokens-per-minute quotas and
  may need the one-time Anthropic use-case form in the console. The org account
  may also need a quota increase before 20 concurrent users.
- Verify model and inference-profile IDs in the account; do not guess them.

## Phases (the issue's six tasks)

- [x] 0. Pared-down environment: `.venv`, `requirements.txt`, `env.sh`, AWS CLI v2,
      session-manager-plugin.
- [ ] 1. `aws login --profile litellm-poc`; read-only inspection of the account:
      identity and permissions, Bedrock Claude models and inference profiles in
      us-west-2, model access, quotas, default VPC, existing resources. Report
      before creating anything.
- [ ] 2. Final proposal with exact resources and costs — **pause for approval**.
- [ ] 3. Build: CloudFormation template + compose file, secrets in Parameter Store.
- [ ] 4. One model under a simple LiteLLM alias (verified IDs).
- [ ] 5. Temporary test key (small budget, expiry); Claude Code on the hub through
      the tunnel; confirm usage shows in LiteLLM.
- [ ] 6. Docs: scaling to ~20 keys, disabling keys, teardown.
