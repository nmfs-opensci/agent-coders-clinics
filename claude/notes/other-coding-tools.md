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
- **Caching fix** (`cache_control_injection_points` on the three Claude models):
  not started. Through OpenAI-style tools Claude gets no caching (Haiku ~$0.02
  every request vs ~$0.005 cached in Claude Code).
