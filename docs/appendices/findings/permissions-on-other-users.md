# IAM Permissions On Other Users

## CreateAccessKey

#### Description

**Creating a new user access key for a different user**: An attacker with the _iam:CreateAccessKey_ permission on other users can create an access key ID and secret access key belonging to another user in the AWS environment, if they don’t already have two sets associated with them (which best practice says they shouldn’t).

## CreateLoginProfile

#### Description

**Creating a new login profile for an IAM user**: An attacker with the _iam:CreateLoginProfile_ permission on other users can create a password to use to login to the AWS console on any user that does not already have a login profile setup.

## UpdateLoginProfile

#### Description

**Updating an existing login profile for an IAM user**: An attacker with the _iam:UpdateLoginProfile_ permission on other users can change the password used to login to the AWS console on any user that already has a login profile setup.

## AddUserToGroup

#### Description

**Adding a user to an Admin group**: An attacker with the _iam:AddUserToGroup_ permission can use it to add themselves to an existing IAM Group in the AWS account.




