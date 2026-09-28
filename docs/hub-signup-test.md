# Testing hub sign-up before the workshop

Run in a JupyterLab terminal, on branch `workshop-key-service`.

```bash
cd ~/agent-coders-clinics
source env.sh
```

## 1. Put the key service on the server

```bash
scripts/keyservice-deploy.sh
```

Last line should be `keyservice: up at https://.../workshop/`.

## 2. Open sign-up with a small cap

```bash
python scripts/workshop.py open --code test-whale --max 2 --hours 1
```

## 3. Sign up as a participant

```bash
~/shared/agent-coders/claude-tester
```

- Type `wrong` first: it should say the code is not right.
- Run it again and type `test-whale`: it should say
  `Got your key for <your hub username>`, then start Claude Code.
- In Claude Code, type `/status`: it should show the gateway URL.
  Quit with `/exit`.

## 4. Check the rest

```bash
claude-tester --budget
python scripts/workshop.py status
```

`status` should list `ws-<your hub username>`. Your own `claude` should still
start with your personal account.

## 5. Clean up

```bash
python scripts/keys.py delete ws-<your hub username>
claude-tester --reset
python scripts/workshop.py close
```

Then open it for real at the workshop (see `docs/organizer.md`).
