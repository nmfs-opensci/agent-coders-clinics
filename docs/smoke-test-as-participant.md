# Smoke test: use the gateway as a participant

Uses the test key `eli-test`, already saved in
`~/agent-coders-clinics/secrets/eli-test.key`.

Open a **new** terminal (File → New → Terminal) and run these in order.

## 1. Clear your usual Claude setup

Every new terminal on this hub sets `CLAUDE_CODE_USE_BEDROCK` and
`ANTHROPIC_API_KEY`, which would send Claude Code around the gateway.

```bash
unset CLAUDE_CODE_USE_BEDROCK ANTHROPIC_API_KEY
```

## 2. Load the key (it is never shown on screen)

```bash
export ANTHROPIC_AUTH_TOKEN=$(cat ~/agent-coders-clinics/secrets/eli-test.key)
```

## 3. Point Claude Code at the gateway

```bash
export ANTHROPIC_BASE_URL=https://18.227.15.211.sslip.io
export ANTHROPIC_MODEL=claude-sonnet-4-6
export ANTHROPIC_DEFAULT_OPUS_MODEL=claude-opus-4-6
export ANTHROPIC_DEFAULT_SONNET_MODEL=claude-sonnet-4-6
export ANTHROPIC_DEFAULT_HAIKU_MODEL=claude-haiku-4-5-20251001
```

## 4. Start Claude Code

```bash
claude
```

Inside it, type `/status`: it should show `https://18.227.15.211.sslip.io`. Then ask
something short.

## 5. Check the spend (organizer view, in another terminal)

Wait about a minute (spend is recorded in batches), then:

```bash
cd ~/agent-coders-clinics
source env.sh
python scripts/keys.py list
```

`eli-test`'s spend should have gone up.

## If something goes wrong

- **Connection refused / timeout**: the gateway server is stopped (`scripts/instance.sh start`).
- **Authentication error**: step 2 did not load the key; check the file exists.
- **No spend on the key**: the request bypassed the gateway, usually because
  step 1 was skipped. Check `/status` shows `https://18.227.15.211.sslip.io`.
