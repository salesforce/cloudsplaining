This policy allows actions that permit modification of [resource-based policies](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_identity-vs-resource.html">) or can otherwise can expose AWS resources to the public via similar actions that can lead to resource exposure.
 
 For example:
 * `s3:PutObjectAcl` grants permission to modify the access control list (ACL) permissions for new or existing objects in an S3 bucket, which could expose objects to rogue actors or to the internet
 * The ability to modify [AWS Resource Access Manager](https://docs.aws.amazon.com/ram/latest/userguide/what-is.html), which could allow a malicious actor to share a VPC hosting sensitive or internal services to rogue AWS accounts
