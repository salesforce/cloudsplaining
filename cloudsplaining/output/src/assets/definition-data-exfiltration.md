This policy contains actions that could allow Data Exfiltration. Data Exfiltration actions allow certain read-only IAM actions without resource constraints, such as `s3:GetObject`, `ssm:GetParameter*`, or `secretsmanager:GetSecretValue`.
 * Unrestricted `s3:GetObject` permissions has a long history of customer data leaks
* `ssm:GetParameter*` and `secretsmanager:GetSecretValue` are both used to access secrets.
* `rds:CopyDBSnapshot` and `rds:CreateDBSnapshot` can be used to exfiltrate RDS database contents.
