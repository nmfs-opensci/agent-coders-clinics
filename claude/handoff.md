# Handoff

## Repo state

Repo for the agent-coders team, Openscapes Champions cohort 2026
(`nmfs-opensci/agent-coders-clinics`). CC0 licensed. Agent instructions live in
`AGENTS.md`; `CLAUDE.md` only imports it. `main` has the LiteLLM gateway
(PR #2, merged 2026-09-25).

## Remind Eli at the start of the next session

Eli asked (2026-09-28) to be reminded of these when coming back:

1. **Delete the test key** `ws-eeholmes-uw` for a clean count before the
   workshop: `python scripts/keys.py delete ws-eeholmes-uw`.
Remove this section once it is done. (The auto mode line was decided
2026-09-28: it went into the skill's hub script and participant quickstart, not
into `claude-tester`, which is being retired.)

## Working on

- **LiteLLM gateway for coding tools on Bedrock** — prototype done (issue #1
  closed), running at `https://18.227.15.211.sslip.io` with per-person keys and
  shared with colleagues. What is running, keys, models, costs:
  `claude/notes/litellm-gateway.md`. Build history and superseded decisions:
  `claude/notes/litellm-gateway-history.md` (on demand).
- **Issue #5 work merged (PR #7, 2026-09-25)**: caching for Claude via
  OpenAI-style tools (live), and `docs/participant-quickstart.md` rewritten for
  **Claude Code, OpenCode and Copilot CLI** (Aider dropped by Eli). Rich
  Signell's PR #6 (set the key first) merged into it; Eli then rearranged the
  basics section by hand. Issue #5 closed 2026-09-25. Details: `claude/notes/other-coding-tools.md`.
- **`agy-agent-coders`, Antigravity for the team on the hub**: merged (PR #13,
  2026-10-03) and installed to `~/shared/agent-coders/`; Eli tested it as a new
  user. Installs agy, adds the team allowlist (R-heavy) and a guard against
  destructive commands to each user's agy settings on every start. Since
  2026-10-03 the guard also blocks pushes to main and repo deletion, and makes
  the agent ask before merges, branch deletes, issue closes and PRs into other
  people's repos. Why it has to work this way, and what is deliberate:
  `claude/notes/agy-launcher.md`.
  PR #14 (2026-10-03, installed): start mode is the `agentMode` key; the
  `defaultMode` it wrote first is ignored by agy, so the launcher now removes it.
  Participant instructions: nmfs-opensci/agent-coders issue #12, merged as that
  repo's PR #14.
- **Issue #9, one-step Claude Code on the JupyterHub**: merged (PR #10,
  2026-09-28); issue still open. A key service on the gateway (`/workshop/key`:
  workshop code + hub username → `ws-<user>` key, $20, 7 days, cap 20) and
  `claude-tester` in `~/shared/agent-coders/`. Live and tested end to end;
  group test 2026-09-29. Details, hub gotchas (login shells, no startup files,
  XDG path, Eli's terminals run as hub account `eeholmes-uw`) and open items:
  `claude/notes/workshop-key-service.md`.
- **Gateway tasks A → #27 → B → C are done** (2026-09-28/29). A: agent-skills
  PR #26; #27: organizer keys, PR #28; B: the template
  `nmfs-opensci/litellm-gateway-template` (its notes live in agent-skills,
  `claude/notes/litellm-gateway-template.md`); plus agent-skills #29 (PR #32),
  gateway setup split from adding a workshop. C: **PR #11 trimmed** to
  `docs/org-install-plan.md` only, short instructions: template + skill, the
  answers for this install, and hand Eli the URL and a revocable **organizer
  key** (never the master key or UI password). Open, not merged; waiting on
  Eli. Eli is trying the template for a real install (2026-09-29). Plan and
  facts: `claude/notes/gateway-skill-tasks.md`.
- **Next task, after 2026-09-30: clean up this repo** (Eli, 2026-09-29). Its
  gateway code and `docs/` are superseded by the skill and the template; what
  stays is for Eli to decide then. Do not start it before.
- Issue #4 still open: real-work cost test, workshop runbook, colleague
  feedback.
- **AWS lessons** (account kinds, logins, member-account roles, per-account
  Bedrock checklist): `claude/notes/aws-setup-lessons.md`.
- The reusable skill exists: `skills/litellm-bedrock-gateway` in
  nmfs-opensci/agent-skills (merged as #24), now the gateway's source of truth.

## Working principles

- Eli is on the Pro plan and clears between tasks rather than compacting: keep
  state in `claude/notes/`, keep notes lean (current facts in one note, history
  in another), work one phase per sitting, keep command output short.
- Always `source env.sh` before AWS commands (it removes the hub's own AWS role).
- Pause before creating any AWS resource that costs money while idle.
- Eli cannot copy reliably from the Claude Code terminal: put commands Eli must
  run in a file under `docs/` and keep lines short.
