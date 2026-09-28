"""Open, close or check workshop sign-up on the key service (keyservice/).

Run after `source env.sh`. Uses the master key from Parameter Store, like keys.py
(or LITELLM_URL and LITELLM_MASTER_KEY_FILE, for an organizer without AWS access):

  python scripts/workshop.py open --code whale-2026 --max 20 --hours 4
  python scripts/workshop.py status
  python scripts/workshop.py close

Participants then run hub/claude-tester and type the code. Each gets a key
named ws-<hub username> with --budget dollars that expires after --days.
Delete a key with `python scripts/keys.py delete ws-<name>` to let that person
sign up again (for example after losing their key file).
"""

import argparse
import datetime as dt
import os
import sys

import requests

from keys import gateway_url, master_key


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--stack", default=os.environ.get("LITELLM_STACK", "litellm-smoke"))
    sub = p.add_subparsers(dest="cmd", required=True)
    o = sub.add_parser("open")
    o.add_argument("--code", required=True, help="said in the room; not case-sensitive")
    o.add_argument("--max", type=int, default=20, help="most workshop keys at once (default 20)")
    o.add_argument("--hours", type=float, default=4, help="sign-up closes after this (default 4)")
    o.add_argument("--budget", type=float, default=20.0, help="USD per key (default 20)")
    o.add_argument("--days", type=int, default=7, help="keys expire after (default 7)")
    sub.add_parser("close")
    sub.add_parser("status")
    args = p.parse_args()

    url = os.environ.get("LITELLM_URL") or gateway_url(args.stack)
    headers = {"Authorization": f"Bearer {master_key(args.stack)}"}
    admin = url.rstrip("/") + "/workshop/admin"

    if args.cmd == "open":
        until = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=args.hours)
        body = {"code": args.code, "max_keys": args.max, "open_until": until.isoformat(timespec="minutes"),
                "budget": args.budget, "days": args.days}
    elif args.cmd == "close":
        body = {"code": ""}
    if args.cmd in ("open", "close"):
        r = requests.post(admin, json=body, headers=headers, timeout=30)
        if not r.ok:
            sys.exit(f"HTTP {r.status_code}: {r.text[:300]}")

    r = requests.get(admin, headers=headers, timeout=30)
    if not r.ok:
        sys.exit(f"HTTP {r.status_code}: {r.text[:300]} (is the key service deployed?)")
    s = r.json()
    ended = s["open_until"] and dt.datetime.fromisoformat(s["open_until"]) < dt.datetime.now(dt.timezone.utc)
    state = "CLOSED" if not s["code"] else f"ENDED at {s['open_until']}" if ended else f"OPEN until {s['open_until']}"
    print(f"Sign-up {state}. Keys: ${s['budget']:g} each, {s['days']} days, "
          f"{len(s['issued'])} of {s['max_keys']} issued.")
    for alias in s["issued"]:
        print("  " + alias)


if __name__ == "__main__":
    main()
