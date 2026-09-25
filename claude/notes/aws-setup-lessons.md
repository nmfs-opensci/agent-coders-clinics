# AWS setup: what we learned (so it need not be relearned)

Written 2026-09-25 after two days of getting Bedrock to answer in a personal
account. The history (dates, error text, account IDs) is in
`litellm-gateway.md`; this note is the distilled lesson, in the order you would
meet the problems again, e.g. when handing over to an ESIP or Openscapes account.

## 1. Kinds of AWS account, and which one you have

- **Classic account** ("Sign up for AWS (advanced)"): root user plus IAM
  users/roles. What most organizations have. The old work-email account `…8846`
  was one.
- **"New experience" account** ("Sign up for AWS (new)", limited release): you
  sign in with an **AWS Builder ID**, work happens in "projects", there are spend
  limits, and **IAM users cannot have console passwords** (humans are the owner
  or invited team members). The project is pinned to one Region by your contact
  country: US → **us-east-2 (Ohio)**.
- **"Activate advanced features"** on a new-experience account is
  **irreversible**. It turns the setup into an **AWS Organization**:
  - a *management account* (billing and admin; keep workloads out of it),
  - the project as a *member account* (AWS named ours "Greenfield Adventures"),
  - an *Identity Delegated Admin* account for IAM Identity Center.
  A region guardrail (SCP) stays attached: most services only in us-east-1,
  us-east-2, us-west-2, and fully only in us-east-2. Bedrock calls are exempt.
  SCPs never apply to the management account itself.
- All accounts in that org share the same root email, so "sign in as root" with
  it always lands in the management account.

## 2. Signing in from the command line (no long-lived keys)

- Use **AWS CLI v2 ≥ 2.32** installed in `~/.local` (PyPI `awscli` is v1 and has
  no `aws login`). From Python, boto3 needs the **`boto3[crt]`** extra to read
  these credentials.
- `aws login --remote --profile litellm-poc` on a machine with no browser (the
  hub): open the printed link on the laptop, sign in with **Builder ID** (not
  root), pick the **Management Account** session, paste the code back, answer
  **No** to the agent-toolkit prompt. Credentials last up to 12 hours.
- Changing the root password invalidates existing `aws login` sessions
  (`LoginRefreshRequired`): just log in again.
- The JupyterHub injects **its own AWS role** (`AWS_ROLE_ARN` + web identity
  token), which the AWS tools use before any profile. `env.sh` unsets it, plus
  `AWS_BEARER_TOKEN_BEDROCK` (a Bedrock API key that would silently send Bedrock
  calls to whatever account made it). Always `source env.sh` first.

## 3. Getting from the management account into a member account

- The management account reaches a member account by **assuming the member's
  `OrganizationAccountAccessRole`**. In `~/.aws/config`:

  ```
  [profile greenfield]
  role_arn = arn:aws:iam::<MEMBER_ID>:role/OrganizationAccountAccessRole
  source_profile = litellm-poc
  region = us-east-2
  ```

  One `aws login` (to `litellm-poc`) then covers every member account.
- Accounts made with **Organizations → Create account** get that role
  automatically (`litellm-smoke-test` did). Accounts **AWS created for you**
  (Greenfield) or that were **invited** do not. Add it from inside the account:
  IAM console → Roles → Create role → *AWS account* → *Another AWS account* =
  management account ID → policy `AdministratorAccess` → name
  `OrganizationAccountAccessRole`. (`scripts/add-org-access-role.sh` does the
  same in CloudShell.) Use the console wizard rather than pasting JSON through a
  terminal: wrapped lines and stray spaces break the policy.
- An "appeal / Something went wrong" page when opening an account is an
  **account-level hold**, not a permissions problem. For Greenfield the cause was
  a missing payment method.

## 4. Before Bedrock will answer: per-account checklist

Work through these **per account**; in an Organization, accounts do not all
inherit each other's settings.

1. **Payment method on the account itself.** Each account in the new-experience
   org needed its own card. Without it Bedrock refuses *every* model, including
   Amazon's own, with `Operation not allowed` (or Error 002 on the old account:
   "Access to Bedrock models is not allowed for this account").
2. **Anthropic First Time Use (use-case) form**, for Claude only. Hard to find in
   the console; submit with `bedrock.put_use_case_for_model_access(formData=...)`
   (JSON: companyName, companyWebsite, intendedUsers, industryOption,
   otherIndustryOption, useCases). In an Organization, submitting it in the
   **management account covers the member accounts**. Missing form →
   `Model use case details have not been submitted`.
3. **Marketplace subscription**: completes automatically on the first Claude
   call, but only from an identity allowed `aws-marketplace:Subscribe`
   (AdministratorAccess is). The gateway's server role cannot do it, so make one
   admin call per model before relying on the server.
4. **New-account verification**: a brand-new account may say "being verified,
   normally takes less than 2 hours". Wait it out.
5. **Quotas** (Service Quotas → Bedrock, tokens per minute). New accounts had
   0 TPM for the newest Claude models; Sonnet 4.6 and Haiku 4.5 had quota.

**Trap: the first-call grace period.** A new account can answer Claude calls for
a while before the form is enforced, then start refusing. A success on day one
proves little; test again later.

**Quick diagnosis**: call a non-Anthropic model too (Amazon Nova, or
`openai.gpt-oss-20b-1:0`). If *it* fails as well, the problem is the account
(payment, hold), not the Anthropic form.

## 5. Bedrock facts worth remembering

- Current Claude models are called through **inference profiles**: `us.` routes
  within US Regions (~10% dearer), `global.` anywhere. Model IDs are verified per
  account with `bedrock.list_inference_profiles`, never guessed.
- **bedrock-mantle** (`https://bedrock-mantle.<region>.api.aws/v1`) is Bedrock's
  OpenAI-compatible endpoint, used with a Bedrock API key and the OpenAI SDK. It
  does not need the Anthropic form, but Claude had 0 quota there; the gateway
  uses the regular `bedrock-runtime` endpoint.
- **Bedrock API keys** are credentials. A *long-term* one silently creates an
  IAM user (`BedrockAPIKey-…`); delete that user when done. Short-term keys
  expire within 12 hours.
- The AWS Pricing API gives exact prices; use it rather than memory when quoting
  costs.

## 6. For the handover to an org account

- Ask what kind of account it is (classic, or new experience with/without
  advanced features) and whether it sits in an Organization with SCPs.
- Run the §4 checklist and `scripts/inspect_account.py` there before deploying.
- Get access by a role you assume from a short-lived login, never an access key.
