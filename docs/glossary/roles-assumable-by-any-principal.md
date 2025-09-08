IAM Roles that can be assumed by any principal (i.e. Principal: '*') present a very high risk and should be remediated immediately.

These configurations are extremely dangerous because they effectively make the role publicly assumable by anyone with valid AWS credentials, regardless of which AWS account they belong to. This creates a critical security vulnerability that can lead to:

- **Unauthorized access**: Any AWS user from any account can assume the role
- **Privilege escalation**: Attackers with minimal AWS access can gain elevated permissions
- **Data breaches**: If the role has access to sensitive resources, those become exposed
- **Compliance violations**: Many security frameworks prohibit such open access patterns

### Common Scenarios Where This Occurs

1. **Misconfigured cross-account access** - Attempting to allow access from multiple accounts but using wildcard instead of specific account IDs
2. **Development/testing shortcuts** - Using overly permissive policies during development that make it to production
3. **Copy-paste errors** - Reusing policy templates without proper customization

### Immediate Remediation Required

Roles with this finding should be considered a **critical security incident** and require immediate attention:

1. **Identify the intended use case** - Determine what legitimate access the role was meant to provide
2. **Replace wildcards with specific principals** - Use exact account IDs, user ARNs, or service principals
3. **Add conditions** - Implement additional constraints like IP restrictions, MFA requirements, or time-based access
4. **Review role permissions** - Ensure the role follows principle of least privilege
5. **Audit access logs** - Check CloudTrail for any unauthorized role assumptions

Unlike roles with conditions that might provide some protection, roles flagged with this finding have **no safeguards** and should be treated as publicly accessible resources.
