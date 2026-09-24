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

## Personal account inspection (2026-09-24, `scripts/inspect_account.py`)

Account `…8846`, profile `litellm-poc` → IAM user `eli-admin`
(AdministratorAccess, console password + MFA, no access keys; created for this
because `aws login` needs a console sign-in and root should not be used).
Findings in us-west-2:

- Not in an AWS Organization, so no organization policies restrict it. All
  build permissions simulate as allowed.
- **No default VPC.** The stack must create its own VPC, public subnet, internet
  gateway and route table (all free).
- Bedrock: every current Anthropic model reports `authorized=AUTHORIZED`,
  `entitled=AVAILABLE`. `agreementAvailability` is `NOT_AVAILABLE`, meaning
  unclear until a real call — a first tiny invocation is the true access test.
- **Tokens-per-minute quotas are 0** for the newest models (Sonnet 5, Opus 5,
  Opus 5.5, Opus 4.7/4.8, Fable 5/5.1) — unusable without a quota increase.
  Usable now: **Sonnet 4.6** (`us.anthropic.claude-sonnet-4-6`, 6M TPM) and
  **Haiku 4.5** (`us.anthropic.claude-haiku-4-5-20251001-v1:0`, 5M TPM); Opus 4.6
  (3M) and Sonnet/Opus 4.5 also have quota. Proposed for the smoke test: Sonnet 4.6
  as the main alias, Haiku 4.5 as Claude Code's small model. Check the org
  account's quotas the same way before the workshop.
- **Blocked: Bedrock refuses every call from this account** (2026-09-24). Tiny
  `converse` calls to Sonnet 4.6, Haiku 4.5, and Amazon's own Nova Micro all
  return `ValidationException: Error 002: Access to Bedrock models is not allowed
  for this account`, repeated on retry. Because Amazon's own model is refused
  too, this is an account-level restriction set by AWS, not an Anthropic form
  or quota issue; the per-model "AUTHORIZED" status above does not reflect it.
  The Free Tier API has no plan record for the account (older account, not on
  the 2025 "free plan"). Fix is on AWS's side: check the payment method in
  Billing, then open a Support case (Account and billing, free on Basic support)
  quoting the error. Do not build infrastructure until a test call succeeds.
  Also found: the Anthropic **First Time Use (use-case) form had not been
  submitted** (`bedrock.get_use_case_for_model_access` → ResourceNotFound).
  Anthropic calls need it regardless; submit it once per account in the Bedrock
  console (model catalog → a Claude model). Marketplace Subscribe/Unsubscribe/
  ViewSubscriptions are allowed via AdministratorAccess. Check the form the
  same way in the org account.
  **Submitted 2026-09-24** via `put_use_case_for_model_access` (JSON form:
  companyName, companyWebsite, intendedUsers "0"=internal/"1"=external/"2"=both,
  industryOption, otherIndustryOption, useCases). Read-back confirmed. Calls
  still returned Error 002 immediately afterwards; AWS allows ~15 min to take
  effect. If still blocked after that, the Support case is the next step.
- Nothing running: no EC2, EBS, Elastic IPs, RDS, CloudFormation stacks, or SSM
  parameters. Leftover IAM roles from Coiled and some Lambda tests — unrelated,
  leave alone.
- Existing AWS Budget `jupyterhub`: $40/month account-wide, alert at 50% actual.
  Month-to-date spend $0. The smoke test fits inside it.

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
- [x] 1. `aws login --profile litellm-poc`; read-only inspection (findings above).
      Rerun `python scripts/inspect_account.py` against the org account later.
- [ ] 2. Final proposal with exact resources and costs — **pause for approval**.
- [ ] 3. Build: CloudFormation template + compose file, secrets in Parameter Store.
- [ ] 4. One model under a simple LiteLLM alias (verified IDs).
- [ ] 5. Temporary test key (small budget, expiry); Claude Code on the hub through
      the tunnel; confirm usage shows in LiteLLM.
- [ ] 6. Docs: scaling to ~20 keys, disabling keys, teardown.
