# Handoff

## Repo state

Repo for the agent-coders team, Openscapes Champions cohort 2026
(`nmfs-opensci/agent-coders-clinics`). CC0 licensed. Agent instructions live in
`AGENTS.md`; `CLAUDE.md` only imports it. `main` has the LiteLLM gateway
(PR #2, merged 2026-09-25).

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
  basics section by hand. Issue #5 is still open: every task in it is done,
  so it can be closed when Eli says. Details: `claude/notes/other-coding-tools.md`.
- **Next open thread: issue #4**: real-work cost test, workshop runbook,
  colleague feedback.
- **AWS lessons** (account kinds, logins, member-account roles, per-account
  Bedrock checklist): `claude/notes/aws-setup-lessons.md`.
- Reusable-skill proposal from this work: nmfs-opensci/agent-skills#22.

## Working principles

- Eli is on the Pro plan and clears between tasks rather than compacting: keep
  state in `claude/notes/`, keep notes lean (current facts in one note, history
  in another), work one phase per sitting, keep command output short.
- Always `source env.sh` before AWS commands (it removes the hub's own AWS role).
- Pause before creating any AWS resource that costs money while idle.
- Eli cannot copy reliably from the Claude Code terminal: put commands Eli must
  run in a file under `docs/` and keep lines short.
