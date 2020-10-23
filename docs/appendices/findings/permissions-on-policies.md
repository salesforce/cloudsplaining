# Permissions On Policies

## CreateNewPolicyVersion

#### Description

**Creating a new policy version to define custom permissions**: An attacker with the _iam:CreatePolicyVersion_ permission can create a new version of an IAM policy that they have access to. This allows them to define their own custom permissions.

## SetExistingDefaultPolicyVersion

#### Description

**Setting the default policy version to an existing version**: An attacker with the _iam:SetDefaultPolicyVersion_ permission may be able to escalate privileges through existing policy versions that are not currently in use.

## AttachUserPolicy

#### Description

**Attaching a higher-privileged policy to a _user_ that they have access to**: An attacker with the _iam:AttachUserPolicy_ permission can escalate privileges by attaching a policy to a user that they have access to, adding the permissions of that policy to the attacker.

## AttachGroupPolicy


#### Description

**Attaching a higher-privileged policy to a _group_ that they have access to**: An attacker with the _iam:AttachGroupPolicy_ permission can escalate privileges by attaching a policy to a group that they are a part of, adding the permissions of that policy to the attacker.

## AttachRolePolicy

#### Description

**Attaching a higher-privileged policy to a _role_ that they have access to**: An attacker with the _iam:AttachRolePolicy_ permission can escalate privileges by attaching a policy to a role that they have access to, adding the permissions of that policy to the attacker.

## PutUserPolicy

#### Description

**Creating/updating an inline policy for a _user_**: An attacker with the _iam:PutUserPolicy_ permission can escalate privileges by creating or updating an inline policy for a user that they have access to, adding the permissions of that policy to the attacker.

## PutGroupPolicy

#### Description

**Creating/updating an inline policy for a _group_**: An attacker with the _iam:PutGroupPolicy_ permission can escalate privileges by creating or updating an inline policy for a group that they are a part of, adding the permissions of that policy to the attacker.

## PutRolePolicy

#### Description

**Creating/updating an inline policy for a _role_**: An attacker with the _iam:PutRolePolicy_ permission can escalate privileges by creating or updating an inline policy for a role that they have access to, adding the permissions of that policy to the attacker.
