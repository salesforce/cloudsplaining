IAM Roles that can be assumed from other AWS accounts can present a greater risk than roles that can only be assumed within the same AWS account. This is especially true if the trusting account is not owned by your organization.

Cross-account role assumption is a common pattern for legitimate use cases such as:
- Service providers accessing customer resources
- Third-party integrations
- Multi-account AWS Organizations setups
- Partner integrations

However, these configurations require careful review to ensure that:
- The external account is trusted and belongs to your organization or a legitimate partner
- The role's permissions are appropriately scoped for the cross-account use case
- Monitoring and logging are in place to track cross-account access
- The trust relationship includes appropriate conditions to limit access scope

Roles flagged with this finding should be reviewed to verify that cross-account access is intentional and properly secured. Pay particular attention to roles that grant broad permissions or access to sensitive resources, as compromise of the external account could lead to unauthorized access to your AWS resources.
