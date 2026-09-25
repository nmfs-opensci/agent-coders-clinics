# Using Claude Code through the workshop gateway

This gateway lets you use Claude Code (and other coding models) on Amazon
Bedrock without an AWS account or an Anthropic subscription. You need two
things from the organizer:

- the **gateway URL**: `https://18.227.15.211.sslip.io`
- a **personal key** (starts with `sk-`), sent to you privately. Keep it to
  yourself: it has its own spending limit and expiry date, and use is recorded
  against it.

## 1. Install Claude Code (skip if you have it)

On macOS, Linux or WSL:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Other options (Homebrew, Windows) are at
<https://code.claude.com/docs/en/setup>. You do not need to log in to Claude.

## 2. Point Claude Code at the gateway

In a terminal, run these lines, putting your key in the second one:

```bash
export ANTHROPIC_BASE_URL=https://18.227.15.211.sslip.io
export ANTHROPIC_AUTH_TOKEN=sk-your-key-here
export ANTHROPIC_MODEL=claude-sonnet-4-6
export ANTHROPIC_DEFAULT_OPUS_MODEL=claude-opus-4-6
export ANTHROPIC_DEFAULT_SONNET_MODEL=claude-sonnet-4-6
export ANTHROPIC_DEFAULT_HAIKU_MODEL=claude-haiku-4-5-20251001
```

If you normally use Claude Code another way (Bedrock, Vertex, or an Anthropic
API key), also clear those settings in this terminal so they do not override
the gateway:

```bash
unset CLAUDE_CODE_USE_BEDROCK CLAUDE_CODE_USE_VERTEX ANTHROPIC_API_KEY
```

These settings last only for this terminal. Open a new terminal and you are
back to your usual setup.

## 3. Start Claude Code

```bash
claude
```

Type `/status` inside Claude Code: it should show the gateway URL above. Then
work as usual.

## Choosing a model

The default is **Claude Sonnet 4.6**. In Claude Code, `/model` switches between
Sonnet, **Opus 4.6** (strongest, about 1.7× the cost) and **Haiku 4.5**
(cheapest Claude).

The gateway also serves open coding models. Switch with `/model <name>`, e.g.
`/model qwen3-coder-480b`:

| Name | Model |
|---|---|
| `qwen3-coder-480b` | Qwen3 Coder 480B |
| `qwen3-coder-30b` | Qwen3 Coder 30B (small, fast) |
| `devstral-2` | Mistral Devstral 2 |
| `kimi-k2.5` | Kimi K2.5 |
| `glm-5` | GLM 5 |
| `minimax-m2.5` | MiniMax M2.5 |
| `deepseek-v3.2` | DeepSeek V3.2 |
| `gpt-oss-120b` | OpenAI GPT-OSS 120B |

These cost a fraction of Claude, but Claude Code is built for Claude, so expect
them to use its tools less reliably.

## Costs

Every request resends Claude Code's instructions and your conversation, about
30,000–60,000 tokens. On Sonnet that is roughly 2–3 cents per request after the
first, and one prompt can make many requests. `/usage` shows what this session
has used.

## What you may see

- **Budget exceeded**: your key has used its spending limit. Ask the organizer.
- **Key expired / blocked**: the key's time is up or it was switched off.
- **Authentication error**: the key in `ANTHROPIC_AUTH_TOKEN` is wrong or
  incomplete; paste it again.
- **Connection refused / timeout**: the gateway server is stopped. Ask the organizer.
