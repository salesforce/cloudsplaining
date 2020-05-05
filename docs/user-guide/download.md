#### Downloading Account Authorization Details

We can scan an entire AWS account and generate reports. To do this, we leverage the AWS IAM [get-account-authorization-details](https://docs.aws.amazon.com/cli/latest/reference/iam/get-account-authorization-details.html) API call, which downloads a large JSON file (around 100KB per account) that contains all of the IAM details for the account. This includes data on users, groups, roles, customer-managed policies, and AWS-managed policies.

* You must have AWS credentials configured that can be used by the CLI.

* You must have the privileges to run [iam:GetAccountAuthorizationDetails](https://docs.aws.amazon.com/IAM/latest/APIReference/API_GetAccountAuthorizationDetails.html). The `arn:aws:iam::aws:policy/SecurityAudit` policy includes this, as do many others that allow Read access to the IAM Service.

* To download the account authorization details, ensure you are authenticated to AWS, then run `cloudsplaining`'s `download` command:

```bash
cloudsplaining download
```

* If you prefer to use your `~/.aws/credentials` file instead of environment variables, you can specify the profile name:

```bash
cloudsplaining download --profile myprofile
```

It will download a JSON file in your current directory that contains your account authorization detail information.

## Additional Details

### Required AWS IAM Policy

Ensure that you have, at minimum, the privileges shown below to run the command successfully.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iam:GetAccountAuthorizationDetails"
      ],
      "Resource": "*"
    }
  ]
}
```
