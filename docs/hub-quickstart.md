# Claude Code on the JupyterHub (workshop)

You need nothing but this hub: no AI account and no AWS account.

## First time

1. Open a terminal: **File → New → Terminal**.
2. Run:

   ```bash
   ~/shared/agent-coders/claude-tester
   ```

3. Type the **workshop code** the organizer gives you.

It gets you a personal key ($20 to spend, lasts 7 days), installs Claude
Code if needed, and starts it. The first start asks a few setup
questions: pick a theme and say yes to trusting the folder.

## After that

```bash
claude-tester
```

Start it in the folder you want to work in, for example `cd ~/my-project`
first.

## Useful

- `claude-tester --budget` shows what you have spent.
- Inside Claude Code: `/model` switches models, for example
  `/model claude-sonnet-4-6`. The default, Haiku, is the cheapest.
- Your key is yours: it is saved in `~/.config/agent-coders/key`
  and use is recorded against it. Do not share it.

## If you have your own Claude account

Keep using `claude` as usual. `claude-tester` keeps its settings and
history in `~/.config/agent-coders/claude` and never touches your own
login or settings in `~/.claude`.

## If something goes wrong

- **"That workshop code is not right"**: check the code and try again.
- **"A key for ... was already issued"**: you, or someone using your
  name, already signed up. Ask the organizer.
- **"All workshop keys are handed out"** or **"sign-up is closed"**: ask
  the organizer.
