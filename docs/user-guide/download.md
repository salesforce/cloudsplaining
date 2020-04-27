# Downloading Account Authorization Details

The `download` command downloads a large JSON file containing all the AWS IAM information in your account. This is done via the [aws iam get-account-authorization-details](https://docs.aws.amazon.com/cli/latest/reference/iam/get-account-authorization-details.html) API call. It stores them in `account-alias.json`.

The `scan` command requires that file.

## Quick start

* Set your AWS access keys as environment variables:

```bash
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
# If you are using MFA or STS; optional but highly recommended
export AWS_SESSION_TOKEN=...
```

* Download the account authorization details

```bash
cloudsplaining download
```

## Additional Details

#### Order of Precedence

* **Environment variables**: The `download` command will first look for the existence of your AWS access keys in environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_SESSION_TOKEN`).
  - Note: If you do not have AWS_SESSION_TOKEN set and are using static access keys, I highly recommend the use of [aws-mfa](https://github.com/broamski/aws-mfa) for security reasons.

* **Shared Credentials file**:
  - If those environment variables are not set, it will then use the `default` profile in your `~/.aws/credentials` file, if a different profile name is not provided via the argument `--profile`.
  - If you specify `--profile all`, it will run the download command recursively for every profile in your `~/.aws/credentials` file.


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
