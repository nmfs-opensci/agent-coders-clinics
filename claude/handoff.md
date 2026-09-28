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
2. **Decide on the auto mode line**: add `export
   CLAUDE_CODE_AUTO_MODE_SERVER=0` to `hub/claude-tester` (then copy it to
   `~/shared-readwrite/agent-coders/`), so participants do not get the
   "this session isn't eligible" notice that pauses Claude Code until Enter.
   Why: comment on issue #9.

Remove this section once both are done.

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
- **Issue #9, one-step Claude Code on the JupyterHub**: merged (PR #10,
  2026-09-28); issue still open. A key service on the gateway (`/workshop/key`:
  workshop code + hub username → `ws-<user>` key, $20, 7 days, cap 20) and
  `claude-tester` in `~/shared/agent-coders/`. Live and tested end to end;
  group test 2026-09-29. Details, hub gotchas (login shells, no startup files,
  XDG path, Eli's terminals run as hub account `eeholmes-uw`) and open items:
  `claude/notes/workshop-key-service.md`.
- **Next: tasks A → B → C, in order, clear between each** (decided
  2026-09-28). A: add workshop sign-up and key management without AWS to the
  `litellm-bedrock-gateway` skill in `nmfs-opensci/agent-skills` (the skill,
  not this repo, is the installer). B: sparse public template repo
  `nmfs-opensci/litellm-bedrock-gateway`. C: minimal instructions for the
  colleague installing in the org account (us-west-2, Eli has no AWS access
  there). Facts, design constraints, and what each task covers:
  `claude/notes/gateway-skill-tasks.md`.
- **PR #11 open, not merged** (branch `org-install-plan`): a long install plan
  from this repo's scripts (superseded by A–C), plus `keys.py`/`workshop.py`
  reading the master key from a file (tested) and `docs/organizer-no-aws.md`.
  Trim or close it in task C.
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
