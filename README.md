# StackSet Enabler

StackSet Enabler deploys the required StackSet roles to your accounts. See the [self-managed permissions](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stacksets-prereqs-self-managed.html) document for more information.

## Workflow

StackSet Enabler does the following:

1. Creates the `AWSCloudFormationStackSetAdministrationRole` role in your current account. 
2. Assumes the `OrganizationAccountAccessRole` role in your child accounts. 
3. Creates the `AWSCloudFormationStackSetExecutionRole` role within each child account.

## Usage

Create an `accounts.txt`, then enter one account number per line. Next, execute the Python script:

```
python enabler.py
```

The script will then log its status:

```
Setting up admin account: 111111111111
Stack has already been deployed in this account
Setting up child account: 222222222222
Asssuming role: OrganizationAccountAccessRole
Extracted credentials from assumed role
Stack has already been deployed in this account
Setting up child account: 333333333333
Asssuming role: OrganizationAccountAccessRole
Extracted credentials from assumed role
Deploying execution stack
```
