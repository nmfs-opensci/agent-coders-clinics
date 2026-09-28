# Running the gateway: organizer steps

Run these in a JupyterLab terminal. First, every time:

```bash
cd ~/agent-coders-clinics
source env.sh
```

If AWS says the session expired, log in again:
`aws login --remote --profile litellm-poc` (Builder ID, choose
**Management Account**, paste the code back, answer **No** to the toolkit prompt).

## Give someone a key

```bash
python scripts/keys.py create esip-tester --budget 5 --days 7
```

- `--budget` is in US dollars; `--days` is how long until it expires.
- Add `--models claude-sonnet-4-6 qwen3-coder-480b` to limit which models it
  may use (default: all). `python scripts/keys.py models` lists them.

The key is saved to `secrets/esip-tester.key` and not shown. To send it,
open that file in JupyterLab, copy the key, and send it **privately** (a direct
message, not a shared channel or email list) together with the gateway URL
and `docs/participant-quickstart.md`.

Gateway URL: `https://18.227.15.211.sslip.io`

## Workshop sign-up on the JupyterHub

People on the hub type `claude-tester`, enter a code you say in the room,
and get their own key: `ws-<hub username>`, $20, 7 days. The participant
page is `docs/hub-quickstart.md`.

Once per server (again after a rebuild or a change to `keyservice/`):

```bash
scripts/keyservice-deploy.sh
```

It should end with `keyservice: up at https://.../workshop/`.
Sign-up stays closed until you open it.

When the workshop starts (the code is not case-sensitive):

```bash
python scripts/workshop.py open --code whale-2026 --max 20 --hours 4
python scripts/workshop.py status
python scripts/workshop.py close
```

`status` lists who has a key. If someone lost their key or took the wrong
name, delete it and they can sign up again:

```bash
python scripts/keys.py delete ws-their-username
```

After changing `hub/claude-tester`, copy it to the shared folder:

```bash
cp hub/claude-tester ~/shared-readwrite/agent-coders/
```

## Watch use and cost

```bash
python scripts/keys.py list
```

Spend appears about a minute after each request.

Or the **Admin UI**: open `https://18.227.15.211.sslip.io/ui`, user `admin`.
The password is in AWS; show it in the terminal only when you need it:

```bash
aws ssm get-parameter --name /litellm-smoke/ui-password \
  --with-decryption --query Parameter.Value --output text
```

## Switch a key off or on, or delete it

```bash
python scripts/keys.py block esip-tester
python scripts/keys.py unblock esip-tester
python scripts/keys.py delete esip-tester
```

## Pause or remove the server

```bash
scripts/instance.sh stop     # ~$5/month while stopped (disk $1.60 + fixed IP $3.60)
scripts/instance.sh start
scripts/teardown.sh          # deletes everything; asks you to confirm
```
