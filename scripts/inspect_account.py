"""Read-only inspection of an AWS account before setting up the LiteLLM gateway.

Run after `source env.sh`:  python scripts/inspect_account.py
Uses whatever profile and Region env.sh selected. Makes no changes and prints
no credentials; account IDs are shortened to their last four digits.
"""

import re
import sys

import boto3
from botocore.exceptions import ClientError

session = boto3.Session()
REGION = session.region_name


def mask(text):
    return re.sub(r"\b\d{8}(\d{4})\b", r"…\1", str(text))


def section(title):
    print(f"\n## {title}")


def attempt(label, fn):
    try:
        return fn()
    except ClientError as e:
        print(f"  {label}: {e.response['Error']['Code']}")
    except Exception as e:  # noqa: BLE001 - report and keep going
        print(f"  {label}: {type(e).__name__}: {e}")
    return None


def identity():
    section("Identity")
    sts = session.client("sts")
    me = sts.get_caller_identity()
    print(f"  profile {session.profile_name}, region {REGION}")
    print(f"  {mask(me['Arn'])}")
    iam = session.client("iam")
    aliases = attempt("account alias", lambda: iam.list_account_aliases()["AccountAliases"])
    if aliases is not None:
        print(f"  account alias: {aliases or 'none'}")
    org = attempt(
        "organization",
        lambda: session.client("organizations").describe_organization()["Organization"],
    )
    if org:
        print(f"  in an AWS Organization (policies there can restrict this account)")
    return me


def permissions(me):
    section("Permissions needed to build the gateway")
    iam = session.client("iam")
    arn = me["Arn"]
    if ":user/" in arn:
        user = arn.split(":user/")[1]
        pols = attempt(
            "attached policies",
            lambda: iam.list_attached_user_policies(UserName=user)["AttachedPolicies"],
        )
        if pols is not None:
            print(f"  attached to {user}: {[p['PolicyName'] for p in pols] or 'none'}")
        groups = attempt("groups", lambda: iam.list_groups_for_user(UserName=user)["Groups"])
        if groups:
            print(f"  groups: {[g['GroupName'] for g in groups]}")
    actions = [
        "cloudformation:CreateStack",
        "ec2:RunInstances",
        "iam:CreateRole",
        "iam:PassRole",
        "ssm:PutParameter",
        "ssm:StartSession",
        "bedrock:InvokeModel",
        "bedrock:ListInferenceProfiles",
    ]
    if ":user/" in arn:
        res = attempt(
            "policy simulation",
            lambda: iam.simulate_principal_policy(
                PolicySourceArn=arn, ActionNames=actions
            )["EvaluationResults"],
        )
        if res:
            for r in res:
                print(f"  {r['EvalActionName']:32} {r['EvalDecision']}")


def bedrock():
    section(f"Bedrock: Anthropic models in {REGION}")
    br = session.client("bedrock")
    models = attempt(
        "list models", lambda: br.list_foundation_models(byProvider="Anthropic")["modelSummaries"]
    )
    for m in models or []:
        status = m.get("modelLifecycle", {}).get("status", "?")
        if status != "ACTIVE":
            continue
        avail = attempt(
            m["modelId"],
            lambda mid=m["modelId"]: br.get_foundation_model_availability(modelId=mid),
        )
        access = ""
        if avail:
            access = (
                f"agreement={avail.get('agreementAvailability', {}).get('status')} "
                f"authorized={avail.get('authorizationStatus')} "
                f"entitled={avail.get('entitlementAvailability')} "
                f"region={avail.get('regionAvailability')}"
            )
        types = ",".join(m.get("inferenceTypesSupported", []))
        print(f"  {m['modelId']:48} [{types}] {access}")

    section(f"Bedrock: Anthropic inference profiles in {REGION}")
    profiles = []
    token = None
    while True:
        kw = {"typeEquals": "SYSTEM_DEFINED", "maxResults": 100}
        if token:
            kw["nextToken"] = token
        page = attempt("list inference profiles", lambda: br.list_inference_profiles(**kw))
        if not page:
            break
        profiles += page["inferenceProfileSummaries"]
        token = page.get("nextToken")
        if not token:
            break
    for p in profiles:
        if "anthropic" not in p["inferenceProfileId"]:
            continue
        regions = sorted(
            {m["modelArn"].split(":")[3] for m in p.get("models", [])}
        )
        print(f"  {p['inferenceProfileId']:52} {p['status']:7} routes to {','.join(regions)}")


def quotas():
    section("Bedrock quotas mentioning Claude tokens per minute (applied values)")
    sq = session.client("service-quotas")
    found = 0
    for page in sq.get_paginator("list_service_quotas").paginate(ServiceCode="bedrock"):
        for q in page["Quotas"]:
            name = q["QuotaName"]
            if "Claude" in name and "tokens per minute" in name.lower():
                found += 1
                print(f"  {q['Value']:>12,.0f}  {name}")
    if not found:
        print("  none applied; defaults are in `list_aws_default_service_quotas`")


def network_and_existing():
    section(f"Network and existing resources in {REGION}")
    ec2 = session.client("ec2")
    vpcs = ec2.describe_vpcs(Filters=[{"Name": "is-default", "Values": ["true"]}])["Vpcs"]
    if vpcs:
        vpc = vpcs[0]["VpcId"]
        subnets = ec2.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc]}])["Subnets"]
        public = [s for s in subnets if s.get("MapPublicIpOnLaunch")]
        print(f"  default VPC present, {len(subnets)} subnets ({len(public)} assign public IPs)")
    else:
        print("  no default VPC")
    offered = ec2.describe_instance_type_offerings(
        LocationType="availability-zone",
        Filters=[{"Name": "instance-type", "Values": ["t4g.small"]}],
    )["InstanceTypeOfferings"]
    print(f"  t4g.small offered in {len(offered)} availability zones")
    inst = [
        i
        for r in ec2.describe_instances()["Reservations"]
        for i in r["Instances"]
        if i["State"]["Name"] != "terminated"
    ]
    print(f"  EC2 instances (not terminated): {len(inst)}")
    for i in inst:
        print(f"    {i['InstanceId']} {i['InstanceType']} {i['State']['Name']}")
    vols = ec2.describe_volumes()["Volumes"]
    eips = ec2.describe_addresses()["Addresses"]
    print(f"  EBS volumes: {len(vols)}, Elastic IPs: {len(eips)}")
    rds = attempt("RDS", lambda: session.client("rds").describe_db_instances()["DBInstances"])
    if rds is not None:
        print(f"  RDS databases: {len(rds)}")
    stacks = session.client("cloudformation").list_stacks(
        StackStatusFilter=[
            "CREATE_COMPLETE", "UPDATE_COMPLETE", "ROLLBACK_COMPLETE",
            "UPDATE_ROLLBACK_COMPLETE", "CREATE_FAILED", "DELETE_FAILED",
        ]
    )["StackSummaries"]
    print(f"  CloudFormation stacks: {[s['StackName'] for s in stacks] or 'none'}")
    params = session.client("ssm").describe_parameters(MaxResults=50)["Parameters"]
    print(f"  SSM parameters: {len(params)}")
    roles = session.client("iam").list_roles()["Roles"]
    custom = [r["RoleName"] for r in roles if not r["Path"].startswith("/aws-service-role/")]
    print(f"  IAM roles (excluding AWS service-linked): {custom or 'none'}")


def billing_guards(me):
    section("Spending guards")
    budgets = attempt(
        "budgets",
        lambda: session.client("budgets", region_name="us-east-1").describe_budgets(
            AccountId=me["Account"]
        ).get("Budgets", []),
    )
    if budgets is not None:
        print(f"  AWS Budgets: {[b['BudgetName'] for b in budgets] or 'none'}")


def main():
    if not session.profile_name or not REGION:
        sys.exit("Run `source env.sh` first.")
    me = identity()
    permissions(me)
    bedrock()
    quotas()
    network_and_existing()
    billing_guards(me)


if __name__ == "__main__":
    main()
