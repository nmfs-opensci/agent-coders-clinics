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
