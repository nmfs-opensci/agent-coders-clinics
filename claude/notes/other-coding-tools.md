# Other coding tools through the gateway (issue #5)

The task list, Copilot CLI setup, and the caching cost table are in issue #5
itself; do not duplicate them here. This note records progress and anything
learned that the issue does not say.

## Status (2026-09-25): all tasks done, merged in PR #7; issue still open

- The gateway answers `/v1/messages`, `/v1/chat/completions` and
  `/v1/responses`.
- **Copilot CLI 1.0.80**: done (installed in `~/.local/bin`). File-reading test
  passed on Haiku, Qwen3 Coder 480B and GPT-OSS 120B.
- **OpenCode 1.18.32**: done (npm, `~/.local/bin/opencode`). Config is an
  `opencode.json` provider using `@ai-sdk/openai-compatible`, `baseURL` the
  gateway `/v1`, `apiKey` `{env:LITELLM_API_KEY}`, and a `models` map. OpenCode
  only knows models listed there ("Model not found" otherwise). Read test
  passed on Haiku, Qwen3 Coder 480B, GPT-OSS 120B; Haiku also wrote a file.
  Qwen 480B once answered "[reads notes.txt]" with an invented number and no
  tool call; told to "use the read tool" it worked twice. `opencode run` in a
  non-terminal shell hangs unless stdin is closed (`</dev/null`).
- **Aider: dropped for now** (Eli, 2026-09-25). The supported tools are
  Claude Code, OpenCode and Copilot CLI. Aider 0.86.2 was installed and then
  removed without being run: Claude
  Code's auto-mode classifier blocked a run with `--yes-always`. If revisited:
  `--model openai/<served name>` with `OPENAI_API_BASE` and `OPENAI_API_KEY`.
- **Quickstart restructure: done (2026-09-25)**, after merging Rich
  Signell's PR #6 (set the key first so the rest pastes unedited). The page
  now sets `GATEWAY_KEY` and `GATEWAY_URL` once; every tool section derives
  its own variables from them. Each tool's block was run as written in a
  clean `HOME` and worked. Copilot CLI needs **no GitHub login** with the
  `COPILOT_PROVIDER_*` variables (checked with an empty home, no token).
  OpenCode config sets `small_model` too, so it never falls back to
  OpenCode's own hosted models. Eli rearranged the basics section after
  that. The model table's costs are input-token price relative to Haiku
  (from the config's prices), with a note that cached Haiku can be as cheap
  per request as the open models.
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
