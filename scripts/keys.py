"""Manage LiteLLM virtual keys for test users, through the tunnel.

Run after `source env.sh`, with scripts/tunnel.sh running in another terminal:

  python scripts/keys.py create alice --budget 2 --days 3
  python scripts/keys.py list
  python scripts/keys.py block alice      # or: unblock alice
  python scripts/keys.py delete alice

The admin (master) key is read from Parameter Store at run time and never
printed. A new key's value is written only to secrets/<user>.key (mode 600,
git-ignored) on this machine; create each user's key on the machine that will
use it, so key values never need copying.
"""

import argparse
import os
import pathlib
import sys

import boto3
import requests

SECRETS = pathlib.Path(__file__).resolve().parent.parent / "secrets"
# Must match SonnetModelName / HaikuModelName in infra/litellm-smoke.yaml.
MODELS = ["claude-sonnet-4-6", "claude-haiku-4-5-20251001"]


def master_key(prefix):
    return boto3.client("ssm").get_parameter(
        Name=f"/{prefix}/master-key", WithDecryption=True
    )["Parameter"]["Value"]


class Gateway:
    def __init__(self, url, prefix):
        self.url = url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {master_key(prefix)}"}

    def call(self, method, path, **kw):
        r = requests.request(method, self.url + path, headers=self.headers, timeout=30, **kw)
        if not r.ok:
            sys.exit(f"{method} {path}: HTTP {r.status_code}: {r.text[:300]}")
        return r.json()

    def keys(self):
        data = self.call("GET", "/key/list", params={"return_full_object": "true", "size": 100})
        return data.get("keys", [])

    def token_for(self, user):
        for k in self.keys():
            if k.get("key_alias") == user:
                return k["token"]
        sys.exit(f"No key with alias {user!r}.")


def create(gw, args):
    path = SECRETS / f"{args.user}.key"
    if path.exists():
        sys.exit(f"{path} already exists; delete the key first.")
    body = {
        "key_alias": args.user,
        "max_budget": args.budget,
        "duration": f"{args.days}d",
        "models": MODELS,
        "metadata": {"purpose": "litellm smoke test"},
    }
    key = gw.call("POST", "/key/generate", json=body)["key"]
    SECRETS.mkdir(exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(key + "\n")
    print(f"Created key for {args.user}: budget ${args.budget}, expires in {args.days} days.")
    print(f"Saved to {path} (not printed).")


def show(gw, args):
    rows = gw.keys()
    if not rows:
        print("No keys.")
    for k in rows:
        print(
            f"{k.get('key_alias') or '-':16} spend ${k.get('spend') or 0:.4f} of "
            f"${k.get('max_budget')}  expires {k.get('expires')}  "
            f"{'BLOCKED' if k.get('blocked') else 'active'}"
        )


def block(gw, args, blocked=True):
    gw.call("POST", "/key/block" if blocked else "/key/unblock", json={"key": gw.token_for(args.user)})
    print(f"{'Blocked' if blocked else 'Unblocked'} {args.user}.")


def delete(gw, args):
    gw.call("POST", "/key/delete", json={"keys": [gw.token_for(args.user)]})
    (SECRETS / f"{args.user}.key").unlink(missing_ok=True)
    print(f"Deleted {args.user}.")


def main():
    ap = argparse.ArgumentParser(description="Manage LiteLLM test keys.")
    ap.add_argument("--url", default=os.environ.get("LITELLM_URL", "http://localhost:4000"))
    ap.add_argument("--prefix", default=os.environ.get("LITELLM_STACK", "litellm-smoke"))
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("create")
    c.add_argument("user")
    c.add_argument("--budget", type=float, default=2.0, help="USD (default 2)")
    c.add_argument("--days", type=int, default=3, help="expiry in days (default 3)")
    sub.add_parser("list")
    for name in ("block", "unblock", "delete"):
        sub.add_parser(name).add_argument("user")
    args = ap.parse_args()

    gw = Gateway(args.url, args.prefix)
    {
        "create": create,
        "list": show,
        "block": block,
        "unblock": lambda g, a: block(g, a, blocked=False),
        "delete": delete,
    }[args.cmd](gw, args)


if __name__ == "__main__":
    main()
