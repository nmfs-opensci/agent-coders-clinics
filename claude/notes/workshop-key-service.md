# Workshop key service and `claude-tester` (plan, 2026-09-28, issue #9)

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
- **Some participants have a personal Claude account and must keep using it.**
  `claude` stays their own; `claude-tester` is the gateway. The wrapper sets
  variables only for the process it starts, never edits `~/.claude/`, and runs
  Claude Code with its own `CLAUDE_CONFIG_DIR` (`~/.config/agent-coders/claude`)
  so gateway sessions never see or disturb the personal login, settings or
  history. This also sidesteps a participant's own `settings.json` `env` block.
- First test with the group: **2026-09-29**, about 10 people plus drop-ins:
  `MAX_KEYS=20`, $20, 7 days.

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
- Check in testing: with a personal login present in `~/.claude/`, both
  `claude` (personal) and `claude-tester` (gateway, `/status`) work afterwards.

## Status (2026-09-28)

- [x] `keyservice/keyservice.py`, tested locally against the live LiteLLM:
      closed, wrong code, bad name, issue, repeat (409), cap, ended. Log holds
      no keys or codes. Admin endpoint (`/workshop/admin`, master key) replaced
      the SSM-written settings file in the plan: `scripts/workshop.py` calls
      it like `keys.py` does.
- [x] `scripts/keyservice-deploy.sh` written (SSM run-command; Caddyfile is
      rewritten in place because it is a single-file bind mount). **Not run:
      Claude's auto mode refused to run it against the live server, so Eli
      runs it** (`docs/hub-signup-test.md`).
- [x] Template: Caddy `/workshop/*` route; `cfn-lint` clean. The service code
      is not in user data; after a rebuild, run `keyservice-deploy.sh`.
- [x] `hub/claude-tester`, copied to `~/shared-readwrite/agent-coders/`.
      Launch tested with a throwaway key in a fake home (Claude answered,
      `--budget` works, personal `~/.claude` untouched). Found: the hub sets
      `XDG_CONFIG_HOME=/etc/xdg/userconfig`, so the script uses `~/.config`
      directly.
- [x] Eli ran `keyservice-deploy.sh` (LiteLLM still healthy after the Caddy
      change) and signed up end to end from hub account **eeholmes-uw**.
      Eli's terminals run as `eeholmes-uw`, a different hub account from the
      `eeholmes` account Claude's sessions run in (visible to Claude under
      `~/allusers/eeholmes-2duw/`), so that was a fresh-participant test.
- Fixes found in that test: a new hub account has **no startup files** and
  `~/.local/bin` is not on the default PATH, and **hub terminals are login
  shells** (`bash -l`: they read `~/.profile`, not `~/.bashrc`). The script now
  adds the PATH line to the login file and `.bashrc`, and puts `~/.local/bin`
  on its own PATH (before, it reinstalled Claude Code on every run).
- **Auto mode notice** ("this session isn't eligible"; holds the first checked
  action until Enter): the gateway cannot be made eligible, because
  server-side review on Bedrock needs Sonnet 5 / Opus 4.7+. Notes on issue #9.
  Suggested, **not applied, waiting on Eli**: `export
  CLAUDE_CODE_AUTO_MODE_SERVER=0` in `claude-tester`.
- Docs: `docs/hub-quickstart.md` (participants), section in
  `docs/organizer.md`, `docs/hub-signup-test.md`.

## Open items (end of 2026-09-28)

- Test key `ws-eeholmes-uw` still exists (delete it for a clean count);
  sign-up is open with the test code until 21:27 UTC, then ends on its own.
- Decide on `CLAUDE_CODE_AUTO_MODE_SERVER=0`; if yes, edit `hub/claude-tester`
  and copy it to `~/shared-readwrite/agent-coders/`.
- Workshop 2026-09-29: `workshop.py open --code <code> --max 20 --hours 4`.
- PR for branch `workshop-key-service` not opened yet.
- Not tested: a first interactive start answering the onboarding questions
  (the participant page guesses at them).
