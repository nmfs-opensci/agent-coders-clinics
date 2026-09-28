# Gateway: skill additions, template repo, org install (tasks A → B → C)

Decided with Eli 2026-09-28. Three tasks, **in this order, with a clear
between each**. Work on the one Eli names; do not run ahead.

## Why

A colleague will install the gateway in the org AWS account. A first plan
(`docs/org-install-plan.md`, PR #11) was written from this repo's scripts, but
the **installer is the `litellm-bedrock-gateway` skill** in
`nmfs-opensci/agent-skills` (merged as agent-skills #24; local clone
`~/agent-skills`; its decisions are in that repo's
`claude/notes/litellm-bedrock-gateway-skill.md`). The skill is the source of
truth. It lacks two things this install needs, so they go into the skill (A),
each install gets a sparse repo from a template (B), and the colleague's
instructions shrink to "use the skill, here are our answers" (C).

## Facts about the org install (from Eli)

- Classic AWS account, normal login (not Builder ID); no org policies block
  Bedrock, IAM roles or Marketplace. **Bedrock never used there**: use-case
  form, quotas and Marketplace calls all needed.
- Region **us-west-2**. No domain (sslip.io).
- JupyterHub sign-up wanted, with the production hub script under its **own
  name and its own key folder**; `claude-tester` stays on the test gateway.
  A shared key folder would hand test-gateway keys to the org gateway.
- **Eli has no AWS access to the org account and will not get any.** Eli runs
  the workshop (open/close sign-up, create/block/delete keys, watch spend)
  from the gateway URL + master key + Admin UI password, sent privately by the
  installer. Installer keeps: start/stop, rebuild, models, key rotation,
  teardown.
- Workshop defaults: $20 per person, 7 days, up to 20 people.

## Task A: add to the skill (PR in agent-skills)

1. **Workshop sign-up**: port `keyservice/keyservice.py`, `scripts/workshop.py`
   and `hub/claude-tester` from this repo. Make the hub script's command
   name, gateway URL and key folder settings (rendered from the deployment's
   settings), so production and test scripts cannot collide.
   Fit the skill's design, not this repo's: the skill keeps the Caddyfile
   and LiteLLM config in SSM Parameter Store and `deploy.sh` runs
   `refresh.sh` on the instance, so the `/workshop/*` route and the key
   service container belong there, not in a separate SSM-push script like
   `scripts/keyservice-deploy.sh`. Issued keys need `user_id` = name (the
   skill's key-isolation fix; `check_gateway.py` checks it).
2. **Organizer without AWS**: the skill's `keys.py` (and `workshop.py`) read
   the master key from a file when a URL and key-file variable are set.
   Already done for this repo's scripts on branch `org-install-plan`
   (`LITELLM_URL` + `LITELLM_MASTER_KEY_FILE`, tested against the live
   gateway with AWS disabled); use the skill's `GATEWAY_*` naming. Carry over
   `docs/organizer-no-aws.md` as a reference page.
3. Hub gotchas to keep (from `workshop-key-service.md`): login shells, no
   startup files on new accounts, `XDG_CONFIG_HOME=/etc/xdg/userconfig`,
   own `CLAUDE_CONFIG_DIR` so a personal Claude login is untouched.
4. Test in a throwaway stack (skill note: distinct `GATEWAY_STACK`, never
   `litellm-smoke`), tear it down. Ask before creating it (costs money).

## Task B: template repo `nmfs-opensci/litellm-bedrock-gateway`

Public GitHub **template** repo, **sparse** (Eli's call; the code stays in the
skill, option 1). Roughly: README (what it is, "Use this template", then load
the skill and run its `init_deployment.sh` into this repo), `AGENTS.md`
pointing the agent at the skill, the skill's `.gitignore`, `LICENSE` (read
`~/.claude/templates/reuse/POLICY.md` first), a `claude/` notes folder for the
install's record. Rejected for now: moving the code into the template and
thinning the skill (option 2); revisit if the code outgrows the skill.

## Task C: the colleague's instructions, minimal

Rewrite `docs/org-install-plan.md` as short instructions: make the org's repo
from the template, install the skill, give the agent the facts above, stop
before anything billed, hand Eli the three items privately. Then decide PR
#11: trim to what is still needed here or close it.

## Other threads from the same session

- Eli's test gateway (Greenfield, `litellm-smoke`): torn down about a week
  after the production one works. After the 2026-09-29 workshop Eli may make
  a repo from the template for a tester; no need to migrate the current one.
- Personal vs org skills: keep `nmfs-opensci/agent-skills` org-only; personal
  skills could live in `~/claude-config` (`claude/skills/`, linked by
  `bootstrap.sh`). Suggested, not decided or started.
