# AGENTS.md

This file provides guidance to AI coding agents (Claude Code, Antigravity,
Codex, Cursor, Copilot, and others) when working with code in this repository.
`CLAUDE.md` contains only `@AGENTS.md`, so Claude Code reads this file too;
edit `AGENTS.md`, not `CLAUDE.md`.

## What this repository is

Repo for the agent-coders team in the Openscapes Champions cohort 2026
(`nmfs-opensci/agent-coders-clinics` on GitHub).

Read `claude/handoff.md` first for the current state of work. The LiteLLM
gateway for Claude Code on Amazon Bedrock (issue #1, merged in PR #2) is
described in `claude/notes/litellm-gateway.md`, which records the decisions,
environment gotchas, and phase checklist.

## Environment

Use only the pared-down project environment, not the hub's large default image:
`.venv` built from `requirements.txt` (setup steps are in `README.md`), with AWS
CLI v2 and `session-manager-plugin` in `~/.local/bin`.

Run `source env.sh` before every AWS command. It removes the JupyterHub's own
AWS role, which the AWS tools would otherwise use first, and selects the
`greenfield` profile in `us-east-2`: a role in the `Greenfield Adventures`
member account, assumed with the `litellm-poc` login to the organization's
management account. Each agent shell command starts fresh, so prefix commands:
`source env.sh && aws sts get-caller-identity`. If credentials have expired, the
user renews them with `aws login --remote --profile litellm-poc`.

Never print or commit AWS credentials, the LiteLLM master key, or participant
keys. Ask before creating AWS resources that cost money while idle.
