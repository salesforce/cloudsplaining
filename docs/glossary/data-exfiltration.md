Data Exfiltration actions allow certain read-only IAM actions without resource constraints, such as `s3:GetObject`, `ssm:GetParameter*`, or `secretsmanager:GetSecretValue`. It also covers Write-level actions that copy a whole data store into a snapshot or export, such as `rds:CreateDBSnapshot`, `ec2:CreateSnapshot`, or `dynamodb:ExportTableToPointInTime`.

 * Unrestricted `s3:GetObject` permissions has a long history of customer data leaks
* `ssm:GetParameter*`, `ssm:GetParameterHistory` and `secretsmanager:GetSecretValue` are used to access secrets.
* `rds:CopyDBSnapshot` and `rds:CreateDBSnapshot` can be used to exfiltrate RDS database contents.

The full list of actions flagged under this category:

* Read: `s3:GetObject`, `ssm:GetParameter`, `ssm:GetParameters`, `ssm:GetParametersByPath`, `ssm:GetParameterHistory`, `secretsmanager:GetSecretValue`
* Snapshot, copy and export: `rds:CreateDBSnapshot`, `rds:CopyDBSnapshot`, `rds:CreateDBClusterSnapshot`, `rds:CopyDBClusterSnapshot`, `rds:StartExportTask`, `ec2:CreateSnapshot`, `ec2:CreateSnapshots`, `ec2:CopySnapshot`, `ec2:CreateInstanceExportTask`, `ec2:ExportImage`, `dynamodb:ExportTableToPointInTime`
