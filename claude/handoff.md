# Handoff

## Repo state

Repo for the agent-coders team, Openscapes Champions cohort 2026
(`nmfs-opensci/agent-coders-clinics`). CC0 licensed. Agent instructions live in
`AGENTS.md`; `CLAUDE.md` only imports it.

## Working on

- **Issue #1: LiteLLM gateway for Claude Code on AWS Bedrock.** Plan, decisions,
  environment setup, and phase checklist: `claude/notes/litellm-gateway.md`.
  Branch `litellm-gateway-setup`.

## Working principles

- Eli compacts often and is on the Pro plan: keep state in `claude/notes/`, work
  one phase per sitting, keep command output short.
- Always `source env.sh` before AWS commands (it removes the hub's own AWS role).
- Pause before creating any AWS resource that costs money while idle.
