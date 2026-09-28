# Workshop key service and `claude-tester` (plan, 2026-09-28)

Goal: on the JupyterHub, a participant types `claude-tester` in a terminal,
enters a workshop code once, and Claude Code runs through the gateway with
their own budget-capped key. No `sk-` strings are handed out.

## Decisions (Eli, 2026-09-28)

- **Option B**: a code said in the room plus the hub username. Rejected: keys
  made ahead and handed out (A: works, but people paste `sk-` strings), the hub
  token check (C: the token would leave the hub), keys issued by the hub itself (D: needs
  the hub's deployment settings; Eli is admin in the web control panel only).
- **No allowlist for now**, only a cap on how many keys can be out.
- Usernames are GitHub usernames, so they are public. That is fine: the code
  keeps strangers out, and the service **never sends out a key that already
  exists**, so knowing a username gets you nothing. Someone who takes a
  colleague's name shows up at once as "already issued".
- The script lives in `~/shared-readwrite/agent-coders/` (writable only by
  admins); participants run it from `~/shared/agent-coders/`, the same NFS
  folder mounted read-only. **Not `~/shared-public`**, which is mounted
  read-write and on 2i2c hubs is normally writable by every user (not yet
  confirmed with a participant account).
- Claude Code is not in the hub image (Eli's copy is in `~/.local/bin`), so
  the script installs it on first run.

## Server side: `keyservice`

- A Python standard-library script (no packages) run in a stock `python`
  container on the existing `litellm` Docker network, no published port.
  Caddy sends `/workshop/*` to it; everything else still goes to LiteLLM.
- `POST /workshop/key` with `{"code": ..., "user": ...}`:
  1. Refuse if closed: no code set, past `OPEN_UNTIL`, or `MAX_KEYS` reached.
  2. Wrong code: wait ~1 s, then 403. The server handles one request at a time,
     so guessing the code is slow and the key count cannot race.
  3. Check that `user` looks like a GitHub username (letters, digits, hyphens, max 39 characters).
  4. Alias `ws-<user>`. If it exists: 409 "already issued, ask the organizer".
  5. Otherwise call LiteLLM `/key/generate` with the master key: budget, `duration`,
     `metadata.workshop`. Return the key and settings once.
- Count of issued keys = LiteLLM keys whose alias starts with `ws-`
  (from `/key/list`), so a restart loses nothing and deleting a key frees a slot.
- Settings in root-only `/opt/litellm/keyservice.env`: master key, code,
  `MAX_KEYS`, `OPEN_UNTIL`, `BUDGET` (default 20), `DAYS` (default 7). Stop the
  container and the endpoint returns an error; nothing else is affected.
- Organizer command (new, e.g. `scripts/workshop.py open|close|status`) sets
  these over SSM without the master key ever leaving the server: the service
  reads it from the existing `litellm.env`. Only the code travels, and it is
  not a real secret.
- The running instance is changed over SSM, **and** `infra/litellm-smoke.yaml`
  gets the same container and Caddy route so a rebuild keeps them.
- No new AWS resources and no new idle cost.

## Hub side: `claude-tester` (bash, kept in repo at `hub/claude-tester`)

1. First run from `~/shared/agent-coders/claude-tester`: link itself into
   `~/.local/bin` (already on PATH), so afterwards `claude-tester` works and
   updates to the shared copy take effect.
2. Install Claude Code if `claude` is missing (official install script).
3. Key file `~/.config/agent-coders/key` (mode 600). If missing, ask for the
   code, POST with `$JUPYTERHUB_USER`, save the key. Clear messages for
   403 / 409 / closed.
4. Clear the variables that would send Claude elsewhere (`CLAUDE_CODE_USE_BEDROCK`,
   `CLAUDE_CODE_USE_VERTEX`, `ANTHROPIC_API_KEY`, `AWS_BEARER_TOKEN_BEDROCK`),
   set the gateway URL, key and model variables (Haiku default, as in
   `scripts/claude-gateway.sh`), `exec claude "$@"`.
5. `claude-tester --budget` prints the spend so far and the budget from `/key/info`.
- Known edge case: an `env` block in a participant's own
  `~/.claude/settings.json` could override these. Check during testing.

## Steps (one per sitting)

1. [ ] `keyservice` script + local test against LiteLLM through `scripts/tunnel.sh`.
2. [ ] Deploy to the running instance over SSM (container, Caddy route, env
       file); `scripts/workshop.py`; update the template; `cfn-lint`.
3. [ ] `claude-tester` in the repo; copy to `~/shared-readwrite/agent-coders/`.
4. [ ] End-to-end test as `eeholmes` with `MAX_KEYS=2`: wrong code, first key,
       repeat (409), cap reached, closed window; delete the `ws-` test keys.
       Ideally one run from a second, non-admin hub account.
5. [ ] Participant page (`docs/`, short lines) and organizer steps in `docs/organizer.md`.

## Open questions

- Workshop date, number of people (sets `MAX_KEYS`), and whether $20 / 7 days
  still holds.
- No GitHub issue yet: `gh` is not logged in on this hub.
