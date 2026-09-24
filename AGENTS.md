# AGENTS.md

This file provides guidance to AI coding agents (Claude Code, Codex, Cursor,
Copilot, Gemini CLI, and others) when working with code in this repository.

## What this repository is

Repo for the agent-coders team in the Openscapes Champions cohort 2026
(`nmfs-opensci/agent-coders-clinics` on GitHub).

Current work is issue #1, a LiteLLM gateway for Claude Code on Amazon Bedrock.
Read `claude/handoff.md` first, then `claude/notes/litellm-gateway.md`, which
records the decisions, environment gotchas, and phase checklist.

## Environment

Use only the pared-down project environment, not the hub's large default image:
`.venv` built from `requirements.txt` (setup steps are in `README.md`), with AWS
CLI v2 and `session-manager-plugin` in `~/.local/bin`.

Run `source env.sh` before every AWS command. It removes the JupyterHub's own
AWS role, which the AWS tools would otherwise use first, and selects the
`litellm-poc` profile in `us-west-2`. Each agent shell command starts fresh, so
prefix commands: `source env.sh && aws sts get-caller-identity`.

Never print or commit AWS credentials, the LiteLLM master key, or participant
keys. Ask before creating AWS resources that cost money while idle.
