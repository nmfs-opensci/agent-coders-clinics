# LiteLLM gateway: current state

Goal: a workshop of ~20 people runs coding tools through
**tool → LiteLLM proxy → Amazon Bedrock**, each person holding a temporary
LiteLLM virtual key with its own budget and expiry, while the only AWS access is
a role on the server. Not the ESIP 2026 pattern (one shared IAM key, no
per-person caps).

This note holds what is true now. How we got here, abandoned accounts and
superseded decisions: `litellm-gateway-history.md` (read only when a question
needs the reasoning). AWS account lessons: `aws-setup-lessons.md`.
Other coding tools (issue #5): `other-coding-tools.md`.

## What is running (2026-09-25)

- Account Greenfield Adventures (…9870), profile `greenfield`, us-east-2.
  Stack `litellm-smoke`, instance `i-02b88c4d367c1b7d3`,
  **`https://18.227.15.211.sslip.io`** (Caddy + Let's Encrypt on an Elastic IP;
  the URL changes if the stack is rebuilt). ~$0.57/day running, ~$5/month
  stopped (the Elastic IP charges while stopped); teardown releases everything.
- PR #2 (gateway) and #3 merged; issue #1 closed. Follow-ups: issue #5 (other
  tools, caching fix), then issue #4 (real-work cost test, workshop runbook,
  colleague feedback). Later: a real domain, org-account handover
  (`aws-setup-lessons.md` §6). Reusable skill proposed: agent-skills#22.
- **Keys live**: `eli-test` ($2, expires 2026-09-28), `esip-tester` ($5, 7
  days, for Rich at ESIP with `docs/participant-quickstart.md`).
- Admin UI `/ui`, user `admin`, password in SSM `/litellm-smoke/ui-password`,
  so the master key is never typed in a browser. The UI is for watching usage
  and cost, **not** for managing models (no `STORE_MODEL_IN_DB`).

## Models

- 11 served, named by Anthropic API IDs so Claude Code recognizes them:
  `claude-sonnet-4-6`, `claude-haiku-4-5-20251001`, `claude-opus-4-6` (via `us.`
  profiles) and, via `bedrock/converse/…`, `qwen3-coder-480b`,
  `qwen3-coder-30b`, `devstral-2`, `kimi-k2.5`, `glm-5`, `minimax-m2.5`,
  `deepseek-v3.2`, `gpt-oss-120b`. Sonnet 5 is not available to the account.
- What is served is `model_list` in the template's user data; the instance role
  allows exactly those models. `keys.py` MODELS must match. Non-Claude prices are
  set explicitly in the config (LiteLLM's catalog had wrong-Region rates).
- User data only runs on first boot: change the running instance by editing
  `/opt/litellm/config.yaml` over SSM and restarting the container, and update
  `infra/litellm-smoke.yaml` too.

## Budget decisions and measured costs (Eli, 2026-09-25)

- Workshop budget **$20 per person for a week**. **Haiku 4.5 is the default**
  (participant docs, `claude-gateway.sh`), **Opus stays on**, **no daily
  allowance** for now (LiteLLM `budget_duration` is the lever).
- Claude Code sends ~34–53k tokens of system prompt and tool definitions per
  request. Session start is a one-time cache write (~$0.13–0.22 Sonnet, ~$0.26
  Opus), then ~$0.02 per Sonnet request. Cache TTL is 5 min, so pauses re-pay
  the start. `/compact` does not help: the bulk is fixed. Estimate $3–8 per
  person-hour on Sonnet.
- Spend reaches LiteLLM's database in batches, ~1 minute late. LiteLLM checks
  the budget before a request, so one request can overshoot slightly.
- Participants check their budget with `GET /key/info` (curl line in the
  quickstart). `/key/info?key=<hash>` of another key returns 200 (LiteLLM
  behavior; hashes are not discoverable); could be blocked in Caddy later.

## Gotchas

- Claude Code → gateway: `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN` (LiteLLM
  key), `ANTHROPIC_MODEL`, and `ANTHROPIC_DEFAULT_HAIKU_MODEL` set to a served
  name — background calls use the small model and fail otherwise.
  `CLAUDE_CODE_USE_BEDROCK` must be unset (Eli's `claude-bedrock` sets it).
- A new account needs one admin `converse` call per Claude model to complete the
  Marketplace subscription; the instance role cannot trigger it.
- Check health with SSM run-command (`/health/readiness`), not by reading logs
  (logs can contain the DB URL).
- Verify model and inference-profile IDs in the account; do not guess them.
- Development check: `pip install -r requirements-dev.txt` then
  `cfn-lint infra/litellm-smoke.yaml`.

## Phases of issue #1

- [x] 0–5: environment, account inspection, approved proposal, build (one
      CloudFormation stack with HTTPS), 11 models, test key with budget/expiry.
- [ ] 6. Docs: largely covered by `docs/organizer.md`; still to write a
      20-person runbook and budget advice from the real-work measurement (#4).
