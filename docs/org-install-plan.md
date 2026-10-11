# Installing the gateway in an organization's AWS account

For the colleague who installs the LiteLLM gateway in the organization's AWS
account, and for their coding agent. Eli Holmes runs the workshops on it but
has **no AWS access to that account and will not get any**.

The installer is the
[`litellm-bedrock-gateway`](https://github.com/nmfs-opensci/agent-skills/tree/main/skills/litellm-bedrock-gateway)
skill. It holds the steps, the account checks and the security rules, and it
asks before anything is billed. This page only says how to start and gives the
answers the skill will ask for.

## 1. Make the install repository

Click **Use this template** on
[nmfs-opensci/litellm-gateway-template](https://github.com/nmfs-opensci/litellm-gateway-template)
and make a repository for this gateway, in whichever GitHub organization suits
you. **Eli needs read access to it**: workshops are run from a clone of it.
It may be public; the gateway URL and every key stay in git-ignored files.

## 2. Install the skill and start

Follow "Get started" in that repository's README: install the skill for your
agent, start the agent in your copy, and say:

```text
Set up a LiteLLM gateway to Amazon Bedrock.
```

## 3. Answers to the skill's setup questions

Give your agent these (from Eli, 2026-09-28):

- **Account**: a **classic** AWS account, normal login (not Builder ID, not
  the "new experience"). The organization has no policies blocking Bedrock,
  IAM roles or AWS Marketplace. You sign in with your own admin access; the
  skill shows how, without long-lived keys.
- **Bedrock has never been used in this account**, so every item of the
  skill's Bedrock readiness checklist applies: the Anthropic use-case form,
  quotas, and one call per Claude model to finish the Marketplace
  subscription. Start early: quota increases can take days.
- **Region**: `us-west-2`. The skill checks which models exist there and
  their prices.
- **Domain**: none; use `sslip.io`.
- **Admin UI**: your choice; only you use it.
- **JupyterHub sign-up**: yes. The hub script needs **its own command name**,
  not `claude-tester`, which stays on Eli's test gateway (the name also names
  the key folder, and a shared one would hand test-gateway keys to this
  gateway). Ask Eli for the name. Hub folders: `~/shared/agent-coders`
  (participants) and `~/shared-readwrite/agent-coders` (admin copy).

The skill stops and asks before it deploys. It costs about $0.57 a day while
running and about $5 a month stopped, plus Bedrock use.

## 4. Hand over to Eli

When the gateway is deployed and verified:

1. Make Eli an **organizer key** (in your copy, after `source gateway.env`):

   ```bash
   python scripts/keys.py organizer create eli
   ```

   It is saved to `secrets/org-eli.key` and not printed.
2. Commit and push the install repository (`docs/` and `hub/` included;
   `secrets/` is ignored).
3. Send Eli **privately** (a direct message or a password manager, never an
   email list, issue or shared channel) two things: the gateway URL from
   `secrets/gateway-url` and the organizer key from `secrets/org-eli.key`.

**Do not send the master key or the Admin UI password.** Neither can be
revoked. The organizer key can: if it leaks,
`python scripts/keys.py organizer revoke eli` stops it at once, then make a
new one. Eli's setup is `docs/organizer-no-aws.md` in the install repository.

## 5. Workshops

Workshops are added one at a time once the gateway runs, each with its own
name, budget and dates. Eli will say when; ask your agent, for example:

```text
Set up a workshop named "orca" with organizer "eli".
```

The first is planned at $20 per person, keys lasting 7 days, up to 20 people.
Eli opens and closes sign-up.

## What stays with you

Eli does everything else without AWS. Only you can start the gateway before a
workshop and stop it after, add or remove models, make or revoke organizer
keys, rebuild, and tear it down. Agree how Eli will reach you before a
workshop.
