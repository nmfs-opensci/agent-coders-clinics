# Handoff

## Repo state

Repo for the agent-coders team, Openscapes Champions cohort 2026
(`nmfs-opensci/agent-coders-clinics`). CC0 licensed. Agent instructions live in
`AGENTS.md`; `CLAUDE.md` only imports it. `main` has the LiteLLM gateway
(PR #2, merged 2026-09-25).

## Working on

- **LiteLLM gateway for Claude Code on Bedrock** — prototype done (issue #1
  closed), running at `https://18.227.15.211.sslip.io` with per-person keys and
  shared with colleagues. Follow-up is **issue #4**: real-work cost test,
  workshop runbook, colleague feedback. Start with "Current state" at the top of
  `claude/notes/litellm-gateway.md` (what is running, live keys, next steps).
- **AWS lessons** (account kinds, logins, member-account roles, per-account
  Bedrock checklist): `claude/notes/aws-setup-lessons.md`.
- Reusable-skill proposal from this work: nmfs-opensci/agent-skills#22.

## Working principles

- Eli compacts often and is on the Pro plan: keep state in `claude/notes/`, work
  one phase per sitting, keep command output short.
- Always `source env.sh` before AWS commands (it removes the hub's own AWS role).
- Pause before creating any AWS resource that costs money while idle.
- Eli cannot copy reliably from the Claude Code terminal: put commands Eli must
  run in a file under `docs/` and keep lines short.
