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

Open a **new** terminal (the short name does not work in the terminal
you used the first time), then:

```bash
claude-tester
```

Start it in the folder you want to work in, for example `cd ~/my-project`
first. The full path, `~/shared/agent-coders/claude-tester`, always works.

## Check your spending

```bash
claude-tester --budget
```

It shows what you have spent, your budget and when your key expires.
Spending shows up about a minute after you use Claude.

## Useful
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
