# Privilege Escalation Using AWS Services

## UpdateExistingGlueDevEndpoint

**Updating an existing Glue Dev Endpoint**: An attacker with the _glue:UpdateDevEndpoint_ permission would be able to update the associated SSH public key of an existing Glue development endpoint, to then SSH into it and have access to the permissions the attached role has access to.

