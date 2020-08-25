# Scanning a Single Policy File

You can also scan a single policy file to identify risks instead of an entire account.

```bash
cloudsplaining scan-policy-file --input-file examples/policies/explicit-actions.json
```

The output will include a finding description and a list of the IAM actions that do not leverage resource constraints. If there are instances of the high priority risks - Data Exfiltration, Resource Exposure, or Privilege Escalation - it will report those too.

The output will resemble the following:

<details>
<summary>Example <code>scan-policy-file</code> output</summary>

```console
Issue found: Data Exfiltration
Actions: s3:GetObject

Issue found: Resource Exposure
Actions: ecr:DeleteRepositoryPolicy, ecr:SetRepositoryPolicy, s3:BypassGovernanceRetention, s3:DeleteAccessPointPolicy, s3:DeleteBucketPolicy, s3:ObjectOwnerOverrideToBucketOwner, s3:PutAccessPointPolicy, s3:PutAccountPublicAccessBlock, s3:PutBucketAcl, s3:PutBucketPolicy, s3:PutBucketPublicAccessBlock, s3:PutObjectAcl, s3:PutObjectVersionAcl

Issue found: Unrestricted Infrastructure Modification
Actions: ecr:BatchDeleteImage, ecr:CompleteLayerUpload, ecr:CreateRepository, ecr:DeleteLifecyclePolicy, ecr:DeleteRepository, ecr:DeleteRepositoryPolicy, ecr:InitiateLayerUpload, ecr:PutImage, ecr:PutImageScanningConfiguration, ecr:PutImageTagMutability, ecr:PutLifecyclePolicy, ecr:SetRepositoryPolicy, ecr:StartImageScan, ecr:StartLifecyclePolicyPreview, ecr:TagResource, ecr:UntagResource, ecr:UploadLayerPart, s3:AbortMultipartUpload, s3:BypassGovernanceRetention, s3:CreateAccessPoint, s3:CreateBucket, s3:DeleteAccessPoint, s3:DeleteAccessPointPolicy, s3:DeleteBucket, s3:DeleteBucketPolicy, s3:DeleteBucketWebsite, s3:DeleteObject, s3:DeleteObjectTagging, s3:DeleteObjectVersion, s3:DeleteObjectVersionTagging, s3:GetObject, s3:ObjectOwnerOverrideToBucketOwner, s3:PutAccelerateConfiguration, s3:PutAccessPointPolicy, s3:PutAnalyticsConfiguration, s3:PutBucketAcl, s3:PutBucketCORS, s3:PutBucketLogging, s3:PutBucketNotification, s3:PutBucketObjectLockConfiguration, s3:PutBucketPolicy, s3:PutBucketPublicAccessBlock, s3:PutBucketRequestPayment, s3:PutBucketTagging, s3:PutBucketVersioning, s3:PutBucketWebsite, s3:PutEncryptionConfiguration, s3:PutInventoryConfiguration, s3:PutLifecycleConfiguration, s3:PutMetricsConfiguration, s3:PutObject, s3:PutObjectAcl, s3:PutObjectLegalHold, s3:PutObjectRetention, s3:PutObjectTagging, s3:PutObjectVersionAcl, s3:PutObjectVersionTagging, s3:PutReplicationConfiguration, s3:ReplicateDelete, s3:ReplicateObject, s3:ReplicateTags, s3:RestoreObject, s3:UpdateJobPriority, s3:UpdateJobStatus

```

</details>

.
