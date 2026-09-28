# Plan: install the gateway in an organization's AWS account

This plan is for a coding agent (Claude Code or similar) working with the
person who installs the gateway in **their organization's** AWS account. Hand it
to the agent as: *"Read `docs/org-install-plan.md` and carry it out with me,
one phase at a time."*

What gets built: one CloudFormation stack with a small EC2 instance running
LiteLLM, Postgres and Caddy (HTTPS), plus the workshop key service. People on
the JupyterHub type the workshop script's name (Phase 7), enter a workshop code, and Claude Code runs
through the gateway with their own key, budget and expiry. Nobody but the
installer has AWS access; the instance's role is the only thing that calls
Bedrock.

## Who does what

- **Installer** (the person working with you, the agent): has an admin sign-in to
  the org AWS account. Builds, starts/stops and tears down the gateway.
- **Organizer** (Eli Holmes): runs the workshop. **Has no AWS access and will
  not get any.** Needs, from the installer: the gateway URL, the gateway's
  master key, and the Admin UI password (Phase 8). With those, the organizer
  creates, blocks and deletes keys, opens and closes sign-up, and watches
  spend. The organizer is also a JupyterHub admin and installs the workshop
  script on the hub.

## What is already known (from Eli, 2026-09-28)

- The account is a **classic** AWS account with a normal login (not Builder ID,
  not the "new experience"). Its organization has **no policies blocking**
  Bedrock, IAM roles or AWS Marketplace.
- Region: **us-west-2**.
- **Bedrock has never been used** in this account, so every item of the
  per-account checklist (Phase 3) applies.
- No domain name: the gateway will be `https://<elastic ip>.sslip.io`.
- The **JupyterHub sign-up** (key service) is wanted, with its own hub script
  under a new name (Phase 7); `claude-tester` stays on the test gateway.
- Workshop defaults: $20 per person, keys last 7 days, up to 20 people.

## Get the code

```bash
git clone https://github.com/nmfs-opensci/agent-coders-clinics.git
cd agent-coders-clinics
```

Work on your own branch (Phase 4). The gateway will later move to its own
template repository, `nmfs-opensci/litellm-bedrock-gateway`; until then it
lives here.

## Read first

1. `README.md`: environment setup.
2. `claude/notes/aws-setup-lessons.md`: every AWS problem we hit, in the order
   you meet them. §4 (per-account Bedrock checklist) matters most here.
3. `claude/notes/litellm-gateway.md`: what the gateway serves, costs, gotchas.
4. `claude/notes/workshop-key-service.md`: the sign-up service and hub traps.
5. `docs/organizer.md`: day-to-day running.

**`AGENTS.md` and `env.sh` describe the original author's setup** (profiles
`greenfield` and `litellm-poc`, account "Greenfield Adventures", us-east-2).
Do not use those names or that account. This install uses the installer's own
profile, selected in Phase 2.

## Rules for the agent

- Work **one phase at a time**. At each **STOP**, report what you found and
  wait for the installer to say go on.
- **Never** print, log or commit AWS credentials, the LiteLLM master key, the
  Admin UI password, or anyone's key. Keys go to `secrets/` (git-ignored) and
  are never shown on screen.
- **No long-lived AWS access keys.** Sign in with short-lived credentials
  (IAM Identity Center / SSO, or `aws login`).
- **Ask before creating anything that costs money** (Phase 5).
- Commands the installer must type themselves (logins, anything in a browser):
  put them in a file under `docs/` with short lines.
- If an AWS call fails, try once more before calling it a bug, then check
  `aws-setup-lessons.md` §4 before guessing.

## Phase 0: remaining questions (STOP until answered)

Write the answers, and the facts above, into a new note
`claude/notes/org-install.md`; it becomes this install's record.

1. Account name and ID, and who administers it.
2. How the installer signs in from the command line: IAM Identity Center (SSO)
   or an IAM user with `aws login`? With what role or permission set? The
   build needs CloudFormation, EC2, IAM role creation, SSM Parameter Store,
   SSM Run Command, Bedrock and Service Quotas; `AdministratorAccess` in the
   account is simplest.
3. Is the account a member of an AWS Organization? If so, who can reach the
   management account (it matters for the Anthropic form in Phase 3)?
4. Where the agent is running: a JupyterHub, or a laptop (macOS or Linux)?
5. Stack name: suggest `litellm-<org>` rather than the default `litellm-smoke`.

## Phase 1: tools and Python environment

Follow `README.md` → "Environment setup":

- AWS CLI **v2, version 2.32 or later** (`aws --version`) and
  `session-manager-plugin`. On a hub, install both into `~/.local` as the
  README shows. On a Mac, use the official installers (or Homebrew).
- `.venv` from `requirements.txt` only. On a JupyterHub use
  `/srv/conda/bin/python3.12 -m venv .venv`; elsewhere any Python 3.12.
- Check: `.venv/bin/python -c "import boto3, awscrt"` succeeds.

## Phase 2: sign-in and profile (STOP after it works)

1. Help the installer make a named profile for the account. For SSO, write
   the steps for `aws configure sso` into `docs/org-login.md` and have them
   run it; afterwards `aws sso login --profile <name>` renews it. For an IAM
   user, `aws login --profile <name>` (add `--remote` on a machine without a
   browser).
2. Create a git-ignored `env.local.sh` (add it to `.gitignore`):

   ```bash
   export LITELLM_AWS_PROFILE=<their-profile>
   export LITELLM_AWS_REGION=us-west-2
   export LITELLM_STACK=<stack-name>
   source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
   ```

   From now on every AWS command starts with `source env.local.sh && …`.
   `env.sh` also removes a JupyterHub's own AWS role and any
   `AWS_BEARER_TOKEN_BEDROCK`, which would otherwise take priority.
3. Check: `source env.local.sh && aws sts get-caller-identity` shows the
   **org account**, not a hub's or the author's.

## Phase 3: get Bedrock working in the account (STOP with a report)

Bedrock has never been used here, so expect to do each of these. Start early:
quota increases can take days.

1. `python scripts/inspect_account.py` (read only). It reports identity,
   whether the needed permissions are present, Anthropic models and inference
   profiles in us-west-2, Claude token quotas, the network, spending guards.
2. **Anthropic First Time Use form.** Check whether it is already submitted;
   if not, submit it with `bedrock.put_use_case_for_model_access` (fields in
   `aws-setup-lessons.md` §4; ask the installer for the organization's
   details, do not invent them). If the account is in an Organization, a form
   in the management account covers member accounts.
3. **Quotas.** Service Quotas → Amazon Bedrock: tokens-per-minute and
   requests-per-minute for Claude Sonnet 4.6, Haiku 4.5 and Opus 4.6 (the
   cross-Region `us.` profiles) must be above zero. For 20 people, ask the
   installer whether to request increases; each request is their call.
4. **Marketplace subscription.** With the **installer's own identity**, make one
   small `converse` call to each Claude model, using the `us.` inference
   profile IDs that `inspect_account.py` listed. The first call subscribes the
   account; the gateway's role cannot.
5. **Non-Claude models**: `model_list` in `infra/litellm-smoke.yaml` also
   serves Qwen, Devstral, Kimi, GLM, MiniMax, DeepSeek and gpt-oss. Check which
   exist in us-west-2 (one small call each).
6. If Claude fails, call a non-Anthropic model too: if that fails as well, the
   problem is the account (payment method, hold), not the Anthropic form.
7. Report what works, what is missing, and anything waiting on AWS or an
   admin. Do not continue past a blocker.

## Phase 4: adapt the repository (STOP for review)

Work on a branch, e.g. `org-install`.

1. **Models.** Remove any model not available in us-west-2 in all three
   places, which must match: `model_list` in the template's user data, the
   instance role's `bedrock:InvokeModel` resources in the template, and
   `MODELS` in `scripts/keys.py`. Use IDs that Phase 3 listed; never guess.
2. **Prices.** The non-Claude prices in `model_list` are us-east-2 rates.
   Look up us-west-2 on-demand rates with the AWS Pricing API and update them
   (a model with no price records $0 spend and makes budgets useless).
3. **Hard-coded gateway URL**: the author's URL
   (`https://18.227.15.211.sslip.io`) is in `hub/claude-tester` and `docs/`.
   Leave `hub/claude-tester` alone (it stays on the test gateway); the new
   URL goes into the new script (Phase 7) and the doc copies (Phase 8).
4. `pip install -r requirements-dev.txt` and
   `cfn-lint infra/litellm-smoke.yaml` must be clean.
5. Show the installer the diff.

## Phase 5: deploy (STOP: ask before running)

Tell the installer the cost first: about **$0.57/day** running (t4g.small,
disk, Elastic IP; check us-west-2 rates), about **$5/month** stopped, plus
Bedrock use (a workshop of 20 at $20 each is at most $400). Nothing is charged
after `scripts/teardown.sh`. Get an explicit yes.

1. `source env.local.sh && scripts/deploy.sh`. It creates the secrets in SSM
   Parameter Store under `/<stack>/` (never printed), deploys the stack and
   prints the outputs, including `GatewayUrl`.
2. Wait ~3 minutes for first boot. Check health with SSM Run Command on the
   instance (`curl -s localhost:4000/health/readiness`), not by reading
   container logs, which can contain the database URL.
3. `scripts/keyservice-deploy.sh`; it ends with `keyservice: up at …`.
4. Record stack name, Region, instance ID and `GatewayUrl` in
   `claude/notes/org-install.md`.

## Phase 6: prove it end to end

1. `python scripts/keys.py create <name>-test --budget 2 --days 1`.
2. `scripts/claude-gateway.sh <name>-test -p "say hello"` (needs Claude Code).
   Try each Claude model once (`--model claude-sonnet-4-6`, etc.).
3. After a minute, `python scripts/keys.py list` shows spend on the test key.
4. **Test the organizer's route, without AWS**: in a shell where AWS is not
   configured, set `LITELLM_URL` to the gateway URL and
   `LITELLM_MASTER_KEY_FILE` to a file holding the master key, then run
   `python scripts/keys.py list` and `python scripts/workshop.py status`.
   Delete that file afterwards.
5. The Admin UI at `<GatewayUrl>/ui` (user `admin`, password from
   `aws ssm get-parameter --name /<stack>/ui-password --with-decryption`)
   shows the request.
6. Test Claude again the next day: a new account can answer for a while and
   then start refusing (`aws-setup-lessons.md` §4, "grace period").
7. `python scripts/keys.py delete <name>-test`.

## Phase 7: JupyterHub sign-up

The organizer does the hub side; the agent prepares it.

**Decided (Eli, 2026-09-28):** the production gateway gets its **own script
under a new name**, alongside `claude-tester`, which stays pointed at the
test gateway. Ask the organizer for the name; `<script>` below.

1. Copy `hub/claude-tester` to `hub/<script>` and change, in the copy:
   - `GATEWAY_URL` to the new gateway URL;
   - `DIR` to its own folder, e.g. `$HOME/.config/agent-coders-<script>`.
     **Required:** the key file lives there, and a shared folder would hand
     a test-gateway key to the org gateway (it would be refused);
   - the link it makes in `~/.local/bin` (`claude-tester` → `<script>`);
   - the marker comment it looks for in startup files, and every message and
     usage line that says `claude-tester`.
2. Test it in a throwaway home (`HOME=$(mktemp -d) hub/<script> --budget`
   should say there is no key yet, and must not touch `~/.config/agent-coders`).
   Commit it on the branch.
3. The organizer copies it to `~/shared-readwrite/agent-coders/` on the hub
   (participants run it once as `~/shared/agent-coders/<script>`, then just
   `<script>`).
4. End-to-end test with the organizer: they run
   `python scripts/workshop.py open --code <code> --max 2 --hours 1` (Phase 8
   setup), sign up from a hub account with `<script>`, check `<script> --budget`,
   check `claude-tester` still reaches the test gateway, then close sign-up
   and delete the test key.
5. Participant instructions: a copy of `docs/hub-quickstart.md` for the new
   name and URL.

## Phase 8: hand over to the organizer (who has no AWS access)

1. Give the organizer, **privately** (a direct message or password manager,
   never email lists, issues or chat channels):
   - the gateway URL,
   - the **master key**: `aws ssm get-parameter --name /<stack>/master-key
     --with-decryption --query Parameter.Value --output text`,
   - the **Admin UI password** (`/<stack>/ui-password`, user `admin`).

   Have the installer run these themselves and copy the values; the agent does
   not print them. The master key controls the gateway (all keys, budgets,
   sign-up), not the AWS account.
2. The organizer's side is `docs/organizer-no-aws.md` (already written): save
   the key in a file, set two variables, and use `keys.py` and `workshop.py`
   as usual.
3. What only the installer can do, since it needs AWS: stop/start the
   instance (`scripts/instance.sh`), `keyservice-deploy.sh` after a rebuild,
   change the served models, teardown, and replace a leaked master key.
   Agree on how the organizer reaches the installer before a workshop.
4. Replace the author's URL in the installer's copies of
   `docs/participant-quickstart.md` and `docs/organizer.md`.
5. Finish `claude/notes/org-install.md`: account, Region, stack, URL, what an
   admin had to do, anything that differed from this plan.
6. Offer a pull request with changes that help the next install (fixes to
   this plan, better defaults), kept apart from account-specific values.
