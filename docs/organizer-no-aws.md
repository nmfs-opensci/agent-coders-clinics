# Running a gateway you have no AWS access to

For the organizer of a gateway that someone else installed in their AWS
account (`docs/org-install-plan.md`). You need three things from the
installer, sent privately:

- the gateway URL, e.g. `https://1.2.3.4.sslip.io`
- the gateway's master key (starts with `sk-`)
- the Admin UI password (user `admin`)

## Once: save the key and the URL

1. In JupyterLab, open the folder `agent-coders-clinics/secrets/` (make it if
   it is missing). New file → `org-master.key`. Paste the master key, save.
2. New file in the same folder: `org.sh`, with these two lines (your URL):

   ```bash
   export LITELLM_URL=https://1.2.3.4.sslip.io
   export LITELLM_MASTER_KEY_FILE=~/agent-coders-clinics/secrets/org-master.key
   ```

3. In a terminal, make the key readable only by you:

   ```bash
   chmod 600 ~/agent-coders-clinics/secrets/org-master.key
   ```

`secrets/` is never committed to git.

## Every time

```bash
cd ~/agent-coders-clinics
source env.sh
source secrets/org.sh
```

No AWS login is needed.

Then the commands in `docs/organizer.md` work as usual, on the org gateway:

```bash
python scripts/workshop.py open --code whale-2026 --max 20 --hours 4
python scripts/workshop.py status
python scripts/workshop.py close
python scripts/keys.py list
python scripts/keys.py create someone --budget 5 --days 7
python scripts/keys.py block someone
python scripts/keys.py delete ws-their-username
```

Admin UI: open `<gateway URL>/ui`, user `admin`, the password from the
installer.

## Ask the installer for

- starting the server before a workshop and stopping it after
  (`scripts/instance.sh`),
- anything after a server rebuild (the key service must be redeployed),
- adding or removing models,
- a new master key if this one may have leaked,
- deleting everything at the end.
