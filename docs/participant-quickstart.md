# Using Claude Code through the workshop gateway

You will receive two things from the organizer:

- a **gateway URL** (for the smoke test: `http://localhost:4000`)
- a **personal key** (starts with `sk-`). Keep it private; it has its own
  spending limit and expiry date.

## 1. Point Claude Code at the gateway

In a terminal, paste these lines one at a time, replacing the key:

```bash
export ANTHROPIC_BASE_URL=http://localhost:4000
export ANTHROPIC_AUTH_TOKEN=sk-your-key-here
export ANTHROPIC_MODEL=sonnet
export ANTHROPIC_DEFAULT_OPUS_MODEL=sonnet
export ANTHROPIC_DEFAULT_SONNET_MODEL=sonnet
export ANTHROPIC_DEFAULT_HAIKU_MODEL=haiku
```

If you normally use Claude Code another way (Bedrock, or an Anthropic API key),
also clear those settings in this terminal so they do not override the gateway:

```bash
unset CLAUDE_CODE_USE_BEDROCK ANTHROPIC_API_KEY
```

## 2. Start Claude Code

```bash
claude
```

Inside Claude Code, `/status` shows the gateway URL it is using.

## Smoke-test only: loading the test key without seeing it

On the organizer's hub the test key lives in a file. Instead of pasting it:

```bash
export ANTHROPIC_AUTH_TOKEN=$(cat ~/agent-coders-clinics/secrets/eli-test.key)
```

## What you may see

- **Budget exceeded**: your key has used its spending limit. Ask the organizer.
- **Key expired / blocked**: the key's time is up or it was switched off.
- **Connection refused** (smoke test): the tunnel to the gateway is not running.
