# Cloudsplaining

`cloudsplaining` identifies violations of least privilege in AWS IAM and generates a risk-prioritized HTML report with a triage worksheet.

![](_images/cloudsplaining-report.gif)

## Commands

* `cloudsplaining download` - Download IAM authorization details for an entire AWS account.
* `cloudsplaining create-exclusions-file` - Create an exclusions file to filter out false positives specific to your context.
* `cloudsplaining scan` - Scan the IAM authorization details file; generate an HTML report and a triage worksheet.
* `cloudsplaining scan-policy-file` - Scan a single IAM policy file
* `cloudsplaining --help` - Print help messages and exit.



### Download the Account Authorization Details

We can scan an entire AWS account and generate reports. To do this, we leverage the AWS IAM [get-account-authorization-details](https://docs.aws.amazon.com/cli/latest/reference/iam/get-account-authorization-details.html) API call, which downloads a large JSON file (around 100KB per account) that contains all of the IAM details for the account. This includes data on users, groups, roles, customer-managed policies, and AWS-managed policies.

* To do this, set your AWS access keys as environment variables:

```bash
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
# If you are using MFA or STS; optional but highly recommended
export AWS_SESSION_TOKEN=...
```

* Then run `cloudsplaining`'s `download` command:

```bash
cloudsplaining download
```

* If you prefer to use your `~/.aws/credentials` file instead of environment variables, you can specify the profile name:

```bash
cloudsplaining download --profile default
```

It will download a file titled `default.json` in your current directory.

### Create the Exclusions file

Cloudsplaining tool does not attempt to understand the context behind everything in your AWS account. It's possible to understand the context behind some of these things programmatically - whether the policy is applied to an instance profile, whether the policy is attached, whether inline IAM policies are in use, and whether or not AWS Managed Policies are in use. **Only you know the context behind the design of your AWS infrastructure and the IAM strategy**.

As such, it's important to eliminate False Positives that are context-dependent. You can do this with an exclusions file. We've included a command that will generate an exclusions file for you so you don't have to remember the required format.

You can create an exclusions template via the following command:

```bash
cloudsplaining create-exclusions-file
```

This will generate a file in your current directory titled `exclusions.yml`.

Now when you run the `scan` command, you can use the exclusions file like this:

```bash
cloudsplaining scan --exclusions-file exclusions.yml \
    --file examples/files/example.json \
    --output examples/files/
```

For more information on the structure of the exclusions file, see [Filtering False Positives](#filtering-false-positives)

### Scan the Authorization Details file

Now that we've downloaded the account authorization file, we can scan *all* of the AWS IAM policies with `cloudsplaining`.

Run the following command:

```bash
cloudsplaining scan --exclusions-file exclusions.yml \
    --file examples/files/example.json \
    --output examples/files/
```
