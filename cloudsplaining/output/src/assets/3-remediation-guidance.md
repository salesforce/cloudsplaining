##### Prioritizing Remediation

Depending on the existing workload of the engineering team addressing your concerns, the team might ask to address high priority items first rather than addressing all items, especially if the report is quite large. In this scenario, consider instructing the team to address High Priority Risks and the usage of AWS-Managed Policies first.

**High priority risks**:

These include Privilege Escalation, Data Exfiltration, and Potential Resource Exposure/Permissions management. This report highlights each finding that has these high priority risks.

**Moving from AWS Managed Policies over to custom policies**:

AWS managed policies always include access to `*` resources because AWS provides these same policies universally to all customer accounts. If this report flags  any AWS-managed policies, it means that the account/service owner team will not only have to implement resource constraints - they will have to create a custom IAM policy to do so. To limit this work, it is best to migrate away from the root cause of the problem - using AWS managed policies.

You can then queue the work for remediating the other Customer-managed policies that do not have the High-Priority Risks attributes. Implementing resource ARN constraints for True Positives is still important, since overly permissive "Write" actions can cause modification or deletion of AWS resources by a bad actor with compromised credentials, resulting in downtime.

##### Remediating the Findings

We suggest two options for remediating each finding:

*   Leveraging [Policy Sentry](https://github.com/salesforce/policy_sentry/), courtesy of [Kinnaird McQuade](https://twitter.com/kmcquade3), which generates policies with resource ARN constraints at user-specified access levels automagically.
*   Manually rewriting the policies


###### Leveraging Policy Sentry

For guidance on how to use Policy Sentry, please see the documentation [here](https://github.com/salesforce/policy_sentry/#writing-secure-policies-based-on-resource-constraints-and-access-levels). This is highly suggested - within 10 minutes of learning the tool, creating a secure IAM policy becomes a matter of:

*   Generating the YAML template with `policy_sentry create-template --output-file crud.yml --template-type crud`
*   Literally copying/pasting resource ARNs into the template
*   Running `policy_sentry write-policy --input-file crud.yml`


###### Manually rewriting the IAM Policies

For guidance on how to write secure IAM Policies by hand, see the tutorial [here](https://engineering.salesforce.com/salesforce-cloud-security-automating-least-privilege-in-aws-iam-with-policy-sentry-b04fe457b8dc#6997). Just be aware - you'll spend a lot of time looking at the [AWS Documentation on IAM Actions, Resources, and Condition Keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_actions-resources-contextkeys.html), which can become quite tedious and time-consuming.



