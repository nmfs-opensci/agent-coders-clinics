"""Create the gateway's secrets in SSM Parameter Store, once.

Run after `source env.sh`:  python scripts/make_secrets.py [--prefix litellm-smoke]

Creates SecureString parameters /<prefix>/master-key, db-password, salt-key
and ui-password
with random values if they do not already exist. Existing values are never
overwritten: changing the salt key would make LiteLLM's stored data unreadable.
Values are never printed.
"""

import argparse
import secrets

import boto3
from botocore.exceptions import ClientError

GENERATORS = {
    # LiteLLM expects keys to start with "sk-".
    "master-key": lambda: "sk-" + secrets.token_urlsafe(32),
    # Hex only, so it can sit in a postgresql:// URL without escaping.
    "db-password": lambda: secrets.token_hex(24),
    "salt-key": lambda: "sk-" + secrets.token_urlsafe(32),
    # Admin UI login (user "admin"), separate from the master key.
    "ui-password": lambda: secrets.token_urlsafe(18),
}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--prefix", default="litellm-smoke")
    args = ap.parse_args()
    ssm = boto3.client("ssm")
    for name, make in GENERATORS.items():
        path = f"/{args.prefix}/{name}"
        try:
            ssm.put_parameter(Name=path, Value=make(), Type="SecureString", Overwrite=False)
            print(f"created  {path}")
        except ClientError as e:
            if e.response["Error"]["Code"] != "ParameterAlreadyExists":
                raise
            print(f"exists   {path}")


if __name__ == "__main__":
    main()
