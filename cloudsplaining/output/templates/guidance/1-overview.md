These policies do not practice the principle of least privilege by leveraging resource ARN constraints where possible.

For example, `s3:PutObject` should be restricted to a specific bucket and object path - such as Resource: `arn:aws:s3:::my-bucket/path/*`. IAM Resource ARN constraints are preferable to allowing access to all resources, like `"Resource": "*"`, which would allow the IAM principal to upload an S3 object to any bucket at any path.

This security control is not just limited to the context of S3, however. Other IAM actions, such as `s3:PutObject`, `iam:PassRole`, and `ssm:GetParameter` should always be scoped down to only the resources that they need access to. In the case of a compromise, overly permissive IAM policies can lead to the compromised principal having access to more resources than necessary, which can result in data exfiltration or other damaging post-exploitation activities. To limit the blast radius of compromised credentials, it is imperative to restrict access to only the IAM actions and resource ARNs that are necessary for the IAM principal to function properly.

This report contains details on all the IAM Policies in the given account that do not leverage resource constraints. They have been sorted according to Customer Managed Policies and AWS Managed Policies, respectively.
