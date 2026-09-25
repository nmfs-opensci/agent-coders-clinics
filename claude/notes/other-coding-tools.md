# Other coding tools through the gateway (issue #5)

The task list, Copilot CLI setup, and the caching cost table are in issue #5
itself; do not duplicate them here. This note records progress and anything
learned that the issue does not say.

## Status (2026-09-25)

- The gateway answers `/v1/messages`, `/v1/chat/completions` and
  `/v1/responses`.
- **Copilot CLI 1.0.80**: done (installed in `~/.local/bin`). File-reading test
  passed on Haiku, Qwen3 Coder 480B and GPT-OSS 120B.
- **OpenCode, Aider**: not started.
- **Quickstart restructure**: not started.
- **Caching fix: done (2026-09-25).** `cache_control_injection_points`
  (system message + message index -1) on the three Claude models, in
  `infra/litellm-smoke.yaml` and applied to the running instance over SSM
  (backup at `/opt/litellm/config.yaml.pre-cache`). LiteLLM 1.102.1 stands down
  when the client sets its own markers (checked in its source,
  `integrations/anthropic_cache_control_hook.py`), so Claude Code is unaffected:
  a Claude Code run afterwards worked, first request 36k tokens, $0.05 as before.
  Copilot CLI + Haiku, measured: first request of a session writes the cache
  (~17k tokens, $0.025), later requests read it (~$0.002, was ~$0.02). Two
  Copilot runs seconds apart did not share a cache, so Copilot's prompt likely
  changes per session; each session pays one write.
- Admin one-off for per-request cache numbers: `/spend/logs` with no date
  parameters returns rows (`metadata.usage_object` has
  `cache_read_input_tokens`); with dates it returns daily totals only.
