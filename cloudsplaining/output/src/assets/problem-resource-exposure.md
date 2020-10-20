### What is the problem?

This policy is capable of **Resource Exposure** actions. Resource Exposure actions allow:
1. Modification of resource-based policies (for example: S3 bucket policies or Secrets Manager Policies). An attacker with these privileges can expose the resources to the public by changing the resource-based policy to include `"Principal": "*"`
2. "Write" level permissions to special AWS services that can lead to exposure of resources to unauthorized policies. For example, using AWS Resource Access Manager, an attacker could [share your AWS VPCs with an AWS account](https://docs.aws.amazon.com/ram/latest/userguide/getting-started-sharing.html) owned by the attacker, which could expose your internal company services and resources to the public or to malicious actors.

For more information on resource-based policies, see [the AWS documentation on Identity-based policies vs resource-based policies](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_identity-vs-resource.html).

For a full list of which services support resource-based policies, see the "Resource-based policies" column of [the AWS documentation on AWS services that work with IAM](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_aws-services-that-work-with-iam.html).

 For a list of resources that can be shared with rogue accounts using AWS Resource Access Manager, see the [AWS RAM documentation on Shareable Resources](https://docs.aws.amazon.com/ram/latest/userguide/shareable.html).
