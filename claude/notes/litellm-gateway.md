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
  setting (`LITELLM_AWS_PROFILE`, default `litellm-smoke`).
- **Where it is built (current, 2026-09-25): member account `litellm-smoke-test`
  (…2338, email e2holmes+litellm@gmail.com)**, created with
  `organizations.create_account` from Eli's management account (see "Switching"
  below for how we got here). Created this way so it has
  `OrganizationAccountAccessRole`: profile `litellm-smoke` (in `~/.aws/config`,
  not the repo) assumes that role with `source_profile = litellm-poc`, and
  `env.sh` selects it. `aws login --remote --profile litellm-poc` signs in to
  the management account (Builder ID, choose "Management Account").
- **Region us-east-2.** Originally us-west-2; changed because the org's surviving
  region SCP blocks most services outside us-east-2 (Bedrock calls exempt).
  `us.` inference profiles route across US Regions anyway.
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

## Phase 2 proposal (2026-09-25, awaiting Eli's approval)

Account `litellm-smoke-test`, us-east-2, one CloudFormation stack `litellm-smoke`.

- Network: own VPC + one public subnet + internet gateway + route table (free;
  portable to accounts without a default VPC). Security group with **no
  inbound rules**; outbound HTTPS only.
- EC2 `t4g.small` (ARM), Amazon Linux 2023, 20 GB gp3 encrypted, IMDSv2
  required, auto-assigned public IPv4 (needed to reach Bedrock/SSM/image
  registry without a NAT gateway).
- Instance role: `AmazonSSMManagedInstanceCore` (Session Manager) + inline
  `bedrock:InvokeModel`/`InvokeModelWithResponseStream` on the two `us.`
  inference profiles and their foundation models in us-east-1/us-east-2/us-west-2,
  `ssm:GetParameter` on `/litellm-smoke/*`.
- Docker Compose: LiteLLM (official image, pinned to the current non-prerelease
  version at build time — tags are now plain `v1.10x.y`, the `-stable` suffix
  stopped in May 2026) + Postgres 16 on the instance disk. LiteLLM listens on
  127.0.0.1:4000 only; reached by SSM port forwarding from the hub.
- Secrets: master key, DB password, `LITELLM_SALT_KEY` as SSM SecureString,
  created by a script with random values, never printed (CloudFormation cannot
  create SecureString parameters). Scripts that need the master key read it
  from SSM themselves.
- Models: alias `sonnet` → `bedrock/us.anthropic.claude-sonnet-4-6`, alias
  `haiku` → `bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0`.
- AWS Budget in the new account, $10/month, email alert to Eli.
- Test key: $2 budget, 3-day expiry.
- Costs checked with the AWS Pricing API: t4g.small $0.0168/h, gp3 $0.08/GB-month,
  public IPv4 $0.005/h → ≈ $0.57/day running, ≈ $17.50/month if left on,
  ≈ $1.60/month stopped (disk only; auto-assigned IPv4 is released on stop),
  $0 after teardown. Bedrock `us.` (geographic cross-Region) prices are ~10%
  above `global.`: Sonnet 4.6 $3.30/M input, $16.50/M output, $0.33/M cache
  read; Haiku 4.5 about $1.10/$5.50. A short Claude Code test ≈ $0.20–$1.
- Planned files: `infra/litellm-smoke.yaml`, compose + LiteLLM config,
  `scripts/make_secrets.py`, deploy/stop/teardown scripts, `scripts/keys.py`
  (create/list/block/delete keys; key values only to git-ignored `secrets/`),
  and a launcher that opens the tunnel and starts Claude Code with the gateway
  variables, clearing `CLAUDE_CODE_USE_BEDROCK`, `ANTHROPIC_API_KEY`,
  `ANTHROPIC_BASE_URL` inherited from Eli's Claude launchers.

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

## Switching to a new personal AWS account (2026-09-24)

Eli **abandoned account `…8846`**: it was opened with a work email, and AWS
kept Bedrock blocked account-wide (Error 002, section below) even after the
billing fixes, with the Support case unanswered. The smoke test moves to a
**new account opened with Eli's personal email**. It reuses the same profile
name `litellm-poc` (`aws login` overwrites the old credentials), so `env.sh`
and the scripts are unchanged. Steps for the new account: choose the Paid plan
(the Free plan restricts some services), root MFA, credit card as the default
payment method, an AWS Budget, an IAM user `e2holmes-admin` (same setup as
`eli-admin` in the old account), the Anthropic
use-case form, then run `scripts/inspect_account.py` and a tiny test call
**before** building anything. Whether to close `…8846` (which holds Coiled
roles and a `jupyterhub` budget) is Eli's decision, not part of this work.

**The new account turned out to be AWS's "new experience"** ("Sign up for AWS
(new)": Builder ID login, projects, spend limits; limited release). Facts from
AWS docs (accounts/latest/reference/: sign-in-new, supported-services-sign-up-new,
connect-ai-coding-tool, project-regions, activate-advanced-features), 2026-09-24:

- No IAM users with console access; humans are the owner or invited team
  members. CLI access is `aws login --profile <name>` as the owner, then pick the
  project on AWS's "Choose AWS sessions" page (12-hour credentials, renewable
  for 90 days). The `e2holmes-admin` IAM user is not needed.
- Projects are pinned to one Region by contact country: US → **us-east-2 (Ohio)**,
  not us-west-2. Bedrock read-only APIs work in other Regions; resources stay in
  the project Region.
- **Bedrock is supported but "Global cross-Region inference and Geographic
  cross-Region inference are not supported."** Current Claude models on Bedrock
  are offered only through inference profiles (`us.`/`global.`), so Claude may
  be unusable here. Verify with a real call before deciding.
- Leaving the new experience = "Activate advanced features": needs Paid plan,
  **irreversible**, makes Eli the admin of an AWS Organization + IAM Identity
  Center + a delegated-admin account, and removes spend limits. Heavy for a
  smoke test.
- Also: an org (ESIP/Openscapes) account is most likely a classic account, so a
  classic "Sign up for AWS (advanced)" account is the closer rehearsal.
- **Eli had already activated advanced features** (irreversible) before seeing
  this. So the new setup is an AWS Organization: a management account (admin
  only), the project as a member account (build here), and a delegated-admin
  account for Identity Center. CLI: `aws login --remote`, sign in as Eli (Builder
  ID), choose the **project** session.
- A region SCP **survives activation** (docs: scps-and-rcps-for-projects):
  `RegionFloor` denies everything outside us-east-1, the project Region
  (us-east-2), and us-west-2; `UsEast1Partitional`/`UsWest2Partitional` deny most
  services in those two, but Bedrock invoke/list actions and Marketplace are
  exempt everywhere. So: **build EC2 etc. in us-east-2**; Bedrock calls are
  allowed. No SCP edit needed unless something else is blocked. Editing SCPs is
  done from AWS Settings → Projects → Manage policies (management account).
- Org "agent-coders" (read from the management account, 2026-09-24): accounts
  `agent-coders Management Account` (…8125), `Greenfield Adventures` (…9870,
  the project; build here), `agent-coders Identity Delegated Admin` (…3491). No
  OUs. Root has SCPs `ManagedAccountSecurityControlPolicy`,
  `AdvancedModeRegionRestrictionSecurityControlPolicy`, `FullAWSAccess` and RCP
  `ManagedAccountResourceControlPolicy`. Identity Center (us-east-1) has no
  permission sets; access goes through **Account access manager**
  (boto3 `account-access`, us-east-1): Eli is entitled directly to
  `role/managed/AccountFullAccessRole` in the management account, and via the
  group `865526619870-AdministratorAccess` (Eli is its only member) to the same
  role in Greenfield. So on paper Eli can reach Greenfield, but the console/`aws
  login` refuses it with only "Something went wrong. Think we got it wrong?
  Contact AWS support for help / appeal" — wording of an automated AWS
  restriction or verification hold on the account, not a permissions error.
  Needs a Support case from the management account.
- **Bedrock works from the management account** (2026-09-24, us-east-2): tiny
  `converse` calls to `us.anthropic.claude-sonnet-4-6`,
  `us.anthropic.claude-haiku-4-5-20251001-v1:0` and Nova Micro all returned "ok",
  even though `get_use_case_for_model_access` says the Anthropic form is not on
  file (so the form was not enforced here, at least for now). Management
  account in us-east-2: default VPC with 3 public subnets, t4g.small in 3 AZs,
  nothing running; Claude quotas same as the old account (Sonnet 4.6 6M TPM,
  Haiku 4.5 5M; newest models 0). SCPs never apply to a management account, so
  the region guardrail does not constrain it. Best practice is to keep workloads
  out of the management account; building the smoke test there is Eli's call.
- Getting into Greenfield failed every way tried: console/`aws login` show the
  "appeal" page; from the management account, `sts:AssumeRole` into Greenfield's
  `OrganizationAccountAccessRole` and `managed/AccountFullAccessRole` is denied
  (new-experience accounts lack the usual org access role); and **all three
  accounts share the root email e2holmes@gmail.com**, so root sign-in with it
  lands in the management account, not Greenfield. Setting the management root
  password invalidates existing `aws login` sessions (log in again).
- **Resolution: created member account `litellm-smoke-test`** (2026-09-25) from
  the management account. Assuming its `OrganizationAccountAccessRole` works.
  First test: Sonnet 4.6 answered "ok"; Haiku 4.5 returned "Your account is
  currently being verified… normally takes less than 2 hours" (routine hold on
  a new account). Retest Haiku before building. Greenfield Adventures stays
  unused; a Support case about it is optional.

## Old personal account inspection (2026-09-24, `scripts/inspect_account.py`)

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
  Then confirmed account-wide: the Bedrock console playground gives the same
  error, and so do us-east-1 calls (Nova Micro and Haiku 4.5). Not our IAM user,
  code, Region, or the Anthropic form. Needs an AWS Support case (Account and
  billing).
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
      Redone for the new setup: account `litellm-smoke-test`, us-east-2 (pending
      Haiku verification hold).
      Rerun `python scripts/inspect_account.py` against the org account later.
- [ ] 2. Final proposal with exact resources and costs — **pause for approval**.
- [ ] 3. Build: CloudFormation template + compose file, secrets in Parameter Store.
- [ ] 4. One model under a simple LiteLLM alias (verified IDs).
- [ ] 5. Temporary test key (small budget, expiry); Claude Code on the hub through
      the tunnel; confirm usage shows in LiteLLM.
- [ ] 6. Docs: scaling to ~20 keys, disabling keys, teardown.
