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
  workshop runbook, colleague feedback. **Issue #5**: other coding tools
  (Copilot CLI tested and working; OpenCode, Aider to do), a per-tool
  participant quickstart, and a caching fix for Claude via OpenAI-style tools.
  What is running, keys, models, costs: `claude/notes/litellm-gateway.md`.
  Issue #5 progress: `claude/notes/other-coding-tools.md`. Build history and
  superseded decisions: `claude/notes/litellm-gateway-history.md` (on demand).
- **AWS lessons** (account kinds, logins, member-account roles, per-account
  Bedrock checklist): `claude/notes/aws-setup-lessons.md`.
- Reusable-skill proposal from this work: nmfs-opensci/agent-skills#22.
- **Issue #5 in progress on branch `issue-5-other-tools`** (pushed, no PR yet;
  the rest of #5 goes on the same branch). Done: caching fix for Claude via
  OpenAI-style tools, live on the gateway. Left: OpenCode, Aider, quickstart
  restructure. The branch's `claude/notes/other-coding-tools.md` is current;
  the copy on `main` predates the caching fix.

## Working principles

- Eli is on the Pro plan and clears between tasks rather than compacting: keep
  state in `claude/notes/`, keep notes lean (current facts in one note, history
  in another), work one phase per sitting, keep command output short.
- Always `source env.sh` before AWS commands (it removes the hub's own AWS role).
- Pause before creating any AWS resource that costs money while idle.
- Eli cannot copy reliably from the Claude Code terminal: put commands Eli must
  run in a file under `docs/` and keep lines short.
