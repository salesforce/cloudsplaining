# Comparison to other tools

Cloudsplaining should be viewed as complimentary to all of the tools mentioned below.

In short, its differentiating factors are:

* Identifying lack of resource ARN constraints for modify-level policies, as well as other risk categories
* Digestible presentation of over-privileged IAM policies in a human readable HTML report
* Workflow is tailor-made for quick assessment, team review, and ticket-opening (as shown in the Triage CSV worksheet)
* The detailed triage, remediation, and validation guidance allows technical individuals who are not experts in AWS IAM to handle most issues with account owner teams when triaging and identifying exclusions.
* If you've ever wondered "does this role *truly deserve* to have these privileges or can we scope the permissions down to reduce blast radius in the case of a breach?" Cloudsplaining is tailor-made for addressing this issue.

## Parliament by Duo Labs

[Parliament](https://github.com/duo-labs/parliament) is a command line tool that lints your IAM policies, duplicating much of the functionality in the web console page when reviewing IAM policies in the browser. It has some security scanning features as well.

Parliament adds value beyond Cloudsplaining by its focus on accuracy/syntax, identifying mismatches, support for resource-based policies, and support for Conditions Logic.

Parliament's core functionality targets a zero false positive ideal, which makes it a great fit for CI/CD pipelines. Cloudsplaining seeks to address wide-ranging categories of over-permissioning (Infrastructure Modification, Privilege Escalation, Data Exfiltration, and Resource Exposure). This does result in a higher false positive rating, but when combined with a triaging and exclusion process, this ultimately results in higher coverage and elimination of risk categories.

## Policy Sentry by Salesforce

Cloudsplaining is an **assessment tool** - i.e., a reactive approach. [Policy Sentry](https://github.com/salesforce/policy_sentry/) is a **policy authoring and automation tool** - i.e., a *preventative* tool. Policy Sentry allows you to use a simple YAML template file to abstract the complexity of writing secure IAM Policies, and can be used to remediate the issues that Cloudsplaining discovers.

## Repokid by Netflix


RepoKid is a **policy revocation tool** that was developed by Netflix, and is one of the more mature and battle-tested AWS IAM open source projects. It leverages AWS Access Advisor, which informs you how many AWS services your IAM Principal has access to, and how many of those services it has used in the last X amount of days or months. If you haven’t used a service within the last 30 days, it “repos” your policy, and strips it of the privileges it doesn’t use. It has some advanced features to allow for whitelisting roles and overall is a great tool.

One shortcoming is that AWS IAM Access Advisor only provides details at the service level (ex: S3-wide, or EC2-wide) and not down to the IAM Action level, so the revised policy is not very granular - but it does operate fully on its own without human intervention.

By design, Repokid is not an assessment tool. As such, it does not scan for specific risk categories, generate HTML reports, or identify lack of resource constraints.


## PMapper

PMapper is a pentester-friendly command line tool that analyzes IAM Trust Policies, resource-based policies, and specific privilege escalation API calls to identify specific privilege escalation paths. You can view the relationships in a graph and query permission sets in a REPL.

We recommend the use of PMapper when performing penetration tests against accounts and for validating privilege escalation paths. However, it does not address Infrastructure Modification, Data Exfiltration, or Resource Exposure specifically and does not generate HTML reports.

