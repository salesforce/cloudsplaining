const privilegeEscalationDefinition = '<p>These policies allow a combination of IAM actions that allow a principal with these permissions to escalate their privileges - for example, by creating an access key for another IAM user, or modifying their own permissions. This research was pioneered by Spencer Gietzen at Rhino Security Labs.  Remediation guidance can be found <a href="https://rhinosecuritylabs.com/aws/aws-privilege-escalation-methods-mitigation/">here</a>.</p>'
const dataExfiltrationDefinition = '<div style="text-align:left"><p>Policies with Data Exfiltration potential allow certain read-only IAM actions without resource constraints, such as <code>s3:GetObject</code>, <code>ssm:GetParameter*</code>, or <code>secretsmanager:GetSecretValue</code>. <br> <ul> <li>Unrestricted <code>s3:GetObject</code> permissions has a long history of customer data leaks.</li> <li><code>ssm:GetParameter*</code> and <code>secretsmanager:GetSecretValue</code> are both used to access secrets.</li> <li><code>rds:CopyDBSnapshot</code> and <code>rds:CreateDBSnapshot</code> can be used to exfiltrate RDS database contents.</li> </ul></p></div>'
const resourceExposureDefinition = '<p>Resource Exposure actions allow modification of Permissions to <a href="https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_identity-vs-resource.html">resource-based policies</a> or otherwise can expose AWS resources to the public via similar actions that can lead to resource exposure - for example, the ability to modify <a href="https://docs.aws.amazon.com/ram/latest/userguide/what-is.html">AWS Resource Access Manager</a>.</p>'
const assumableByComputeServiceDefinition = '<p>IAM Roles can be assumed by AWS Compute Services (such as EC2, ECS, EKS, or Lambda) can present greater risk than user-defined roles, especially if the AWS Compute service is on an instance that is directly or indirectly exposed to the internet. Flagging these roles is particularly useful to penetration testers (or attackers) under certain scenarios.<br>For example, if an attacker obtains privileges to execute <code>ssm:SendCommand</code> and there are privileged EC2 instances with the SSM agent installed, they can effectively have the privileges of those EC2 instances.</p>'
const credentialsExposureDefinition = '<p>Credentials Exposure actions return credentials as part of the API response , such as ecr:GetAuthorizationToken, iam:UpdateAccessKey, and others. The full list is maintained here: https://gist.github.com/kmcquade/33860a617e651104d243c324ddf7992a</p>'
const serviceWildcardDefinition = '<p>"Service Wildcard" is the unofficial way of referring to IAM policy statements that grant access to ALL actions under a service - like s3:*. Prioritizing the remediation of policies with this characteristic can help to efficiently reduce the total count of issues in the Cloudsplaining report.</p>'

let riskDefinitions = {
    PrivilegeEscalation: privilegeEscalationDefinition,
    DataExfiltration: dataExfiltrationDefinition,
    ResourceExposure: resourceExposureDefinition,
    AssumableByComputeService: assumableByComputeServiceDefinition,
    CredentialsExposure: credentialsExposureDefinition,
    ServiceWildcard: serviceWildcardDefinition,
}

let riskAlertIndicatorColors = {
    PrivilegeEscalation: 'danger',
    DataExfiltration: 'warning',
    ResourceExposure: 'danger',
    AssumableByComputeService: 'info',
    CredentialsExposure: 'secondary',
    ServiceWildcard: 'primary',
}

let riskDetailsToDisplay = [
    // {
    //     risk_type: "PrivilegeEscalation",
    //     explanation: "Explanation!"
    // },
    {
        risk_type: "CredentialsExposure",
        explanation: "Explanation!"
    },
    {
        risk_type: "DataExfiltration",
        explanation: "Explanation!"
    },
    {
        risk_type: "ResourceExposure",
        explanation: "Explanation!"
    },
    {
        risk_type: "ServiceWildcard",
        explanation: "Explanation!"
    },
    {
        risk_type: "InfrastructureModification",
        explanation: "Explanation!"
    },
]

function getRiskDefinition(riskType) {
    return riskDefinitions[riskType]
}

function getRiskAlertIndicatorColor(riskType) {
    return riskAlertIndicatorColors[riskType]
}

function getRiskDetailsToDisplay() {
    return riskDetailsToDisplay
}

exports.getRiskDefinition = getRiskDefinition;
exports.getRiskAlertIndicatorColor = getRiskAlertIndicatorColor;
exports.getRiskDetailsToDisplay = getRiskDetailsToDisplay;
