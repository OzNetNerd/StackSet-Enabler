import sys
import boto3
from botocore.exceptions import ClientError

ACCOUNTS_FILENAME = "accounts.txt"
CROSS_ACCOUNT_ROLE_NAME = "OrganizationAccountAccessRole"
ROLE_SESSION_NAME = "StackSet_Enabler"
ADMIN_STACK_NAME = "AWSCloudFormationStackSetAdministrationRole"
CHILD_STACK_NAME = "AWSCloudFormationStackSetExecutionRole"
ADMIN_ROLE_TEMPLATE = "https://s3.amazonaws.com/cloudformation-stackset-sample-templates-us-east-1/AWSCloudFormationStackSetAdministrationRole.yml"
EXECUTION_ROLE_TEMPLATE = "https://s3.amazonaws.com/cloudformation-stackset-sample-templates-us-east-1/AWSCloudFormationStackSetExecutionRole.yml"
ADMIN_ACCOUNT_ID = boto3.client("sts").get_caller_identity().get("Account")


def _get_child_account_keys(account_id):
    print(f"Asssuming role: {CROSS_ACCOUNT_ROLE_NAME}")
    sts = boto3.client("sts")
    response = sts.assume_role(
        RoleSessionName=ROLE_SESSION_NAME,
        RoleArn=f"arn:aws:iam::{account_id}:role/{CROSS_ACCOUNT_ROLE_NAME}",
    )

    access_key_id = response["Credentials"]["AccessKeyId"]
    secrect_access_key = response["Credentials"]["SecretAccessKey"]
    session_token = response["Credentials"]["SessionToken"]
    print("Extracted credentials from assumed role")

    return access_key_id, secrect_access_key, session_token


def _deploy_admin_stack():
    print(f"Setting up admin account: {ADMIN_ACCOUNT_ID}")

    client = boto3.client("cloudformation")

    try:
        client.create_stack(
            StackName=ADMIN_STACK_NAME,
            TemplateURL=ADMIN_ROLE_TEMPLATE,
            OnFailure="DELETE",
            EnableTerminationProtection=True,
            Capabilities=["CAPABILITY_NAMED_IAM"],
        )

        print("Deploying admin stack")

    except ClientError as e:
        error_type = e.response["Error"]["Code"]
        if error_type == "AlreadyExistsException":
            print("Stack has already been deployed in this account")

        else:
            message = e.response["Error"]["Message"]
            sys.exit(message)


def _deploy_execution_stack(access_key_id, secrect_access_key, session_token):
    client = boto3.client(
        "cloudformation",
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secrect_access_key,
        aws_session_token=session_token,
    )

    try:
        client.create_stack(
            StackName=CHILD_STACK_NAME,
            TemplateURL=EXECUTION_ROLE_TEMPLATE,
            OnFailure="DELETE",
            EnableTerminationProtection=True,
            Parameters=[
                {
                    "ParameterKey": "AdministratorAccountId",
                    "ParameterValue": ADMIN_ACCOUNT_ID,
                },
            ],
            Capabilities=["CAPABILITY_NAMED_IAM"],
        )

        print("Deploying execution stack")

    except ClientError as e:
        if e.response["Error"]["Code"] == "AlreadyExistsException":
            print("Stack has already been deployed in this account")


def _get_account_list():
    with open(ACCOUNTS_FILENAME) as f:
        account_numbers = f.read().splitlines()

    return account_numbers


def main():
    _deploy_admin_stack()

    account_ids = _get_account_list()
    for account_id in account_ids:
        print(f"Setting up child account: {account_id}")

        access_key_id, secrect_access_key, session_token = _get_child_account_keys(
            account_id
        )

        _deploy_execution_stack(access_key_id, secrect_access_key, session_token)


if __name__ == "__main__":
    main()
