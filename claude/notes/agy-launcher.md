# `agy-agent-coders`: the team's Antigravity launcher (2026-10-03, PR #13)

`hub/agy-agent-coders`, installed to `~/shared/agent-coders/` (copy step in
`docs/organizer.md`). Starts the Antigravity CLI (`agy`) after installing it if
missing, merging the team's allowlist into the user's
`~/.gemini/antigravity-cli/settings.json`, and registering its own `--hook` mode
as a PreToolUse guard in `~/.gemini/config/hooks.json`. Re-applies every start,
so updating the shared copy reaches everyone at their next start. Eli tested it
as a new hub user on 2026-10-03, Google sign-in included: works.

## Why it is built this way (facts found by running agy 1.2.x on the hub)

- **Out of the box agy asks before every command**, and `agy -p` stops the whole
  task at the first one. Without an allowlist it cannot do basic work.
- **Allow rules only work in the user's own settings.json.** A repo's
  `.agents/hooks.json` is loaded and its `"deny"` works, but its `"allow"` (with or
  without `permissionOverrides`) is ignored. No per-repo or admin permissions file
  exists; `/etc` on the hub is wiped anyway. Hence a launcher writing into `~`.
- **Rules match whole words from the start, as literal text**: `command(gh pr view)`
  allows `gh pr view 12`, not `gh pr merge`; every part of `a && b` / `a | b` must
  match; `~` is not expanded in command rules.
- **`curl -fsSL https://antigravity.google/cli/install.sh | bash` fails as
  documented**: the server sends the script gzipped. The launcher uses `--compressed`.
- **`agy --sandbox` does not work on the hub** (`mount proc: operation not
  permitted` in the pod).

## Deliberate choices

- **R, Rscript, quarto, python are allowed** although they run arbitrary code: the
  team is mostly R users and the work needs them. Copy/move/delete, `pip` and
  everything else still ask.
- **Only adds.** Keeps the user's keys, rules and hooks, including an `agentMode`
  they chose (agy's startup mode; it ignores `defaultMode`, which earlier
  versions wrote and the launcher now removes); atomic writes; first change leaves `.before-agent-coders` copies;
  a symlinked hooks file (Eli's, into claude-config) is left alone.
- **The guard stands alone.** Eli's personal guard in `eeholmes/claude-config`
  (`common/hooks/deny-destructive-git.py`) is similar but personalized (it allows
  `rm -r` in the temp dir and follows `VAR=` assignments; the team one refuses
  variable paths). Do not merge them; when Eli's changes, she is asked whether to
  carry the change here. Kept as is on 2026-10-03.
- **GitHub rules carried over from Eli's guard (2026-10-03)**, because `gh auth
  login` lets the agent act on GitHub as the person. Denied: pushing to `main`,
  `master` or the remote's default branch (any form, `--all`/`--mirror`,
  `gh repo sync`, moving the ref with `gh api`), and deleting a repository. "Ask
  first": `gh pr merge`, deleting a branch (`git branch -d/-D`, `git push --delete`
  or `:name`, `--delete-branch`), `gh issue close`, and `gh pr create` into a repo
  the person's `gh` login does not own (or a fork's parent). agy hooks cannot ask, so
  those are denied with a reason telling the agent to ask, then let through on a
  rerun as `USER_CONFIRMED=1 <command>`. agy strips that prefix before matching
  allow rules, so for `git` (allowed) it is only a stop-and-ask the agent honours;
  `gh pr merge`, `gh issue close` and `gh api` are not on the team list, so agy's
  own prompt still follows. The `gh api` merge/close/branch-delete forms are left
  to that prompt rather than the guard.

## Open

- Participant-facing instructions: nmfs-opensci/agent-coders issue #12 (its first
  comment has what to tell people).
