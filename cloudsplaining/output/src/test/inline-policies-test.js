var inlinePolicies = require('../util/inline-policies')
var sampleData = require('../sampleData');
let mocha = require('mocha');
let chai = require('chai');
let it = mocha.it;
let iam_data = sampleData.sample_iam_data;

it("inlinePolicies.getInlinePolicyDocument: should return Inline policy document object", function () {
    var result = inlinePolicies.getInlinePolicyDocument(iam_data, "9dfb8b36ce6c68a741355e7a2ab5ee62a47755f8f25d68e4fa6f87dabc036986");
    var expectedResult = {
        "Version": "2012-10-17",
        "Statement": [
          {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
              "s3:GetObject",
              "s3:PutObjectAcl"
            ],
            "Resource": "*"
          }
        ]
      };
    chai.assert(result != null);
    chai.assert.deepStrictEqual(result, expectedResult);
    console.log(`inline policy document: ${JSON.stringify(result)}`);
});

it("inlinePolicies.getServicesAffectedByInlinePolicy: should identify list of services affected by the policy findings with no duplicates", function() {
    var result = inlinePolicies.getServicesAffectedByInlinePolicy(iam_data, "0e1bd3995cfe6cfbbac133f1406839e6b415e5b5a412cd148ac78071d82e5b1b")
    var expectedResult = [
        "s3",
    ]
    chai.assert(result != null);
    chai.assert.deepStrictEqual(result, expectedResult, "lists of services used do not match")
    console.log(`Services affected: ${JSON.stringify(result)}`);
});


it("inlinePolicies.getInlinePolicyFindings: should return Inline policy findings for PrivilegeEscalation", function () {
    var result = inlinePolicies.getInlinePolicyFindings(iam_data, "aad4a5d1e0cd67fb99c658e1d326f16afd2f6857804f6ffd547c9c13ef508540", "PrivilegeEscalation");
    var expectedResult = []
    chai.assert(result != null);
    chai.assert.deepStrictEqual(result, expectedResult)
    console.log(`PrivilegeEscalation findings: ${JSON.stringify(result)}`);
});

it("inlinePolicies.getInlinePolicyFindings: should return Inline policy findings for ResourceExposure", function () {
    var result = inlinePolicies.getInlinePolicyFindings(iam_data, "aad4a5d1e0cd67fb99c658e1d326f16afd2f6857804f6ffd547c9c13ef508540", "ResourceExposure");
    var expectedResult = [
        "iam:AddRoleToInstanceProfile",
        "iam:CreateInstanceProfile",
        "iam:PassRole"
    ]
    chai.assert(result != null);
    chai.assert.deepStrictEqual(result, expectedResult)
    console.log(`ResourceExposure findings: ${JSON.stringify(result)}`);
});


it("inlinePolicies.getInlinePolicyIds: should print out all inline Policy IDs", function () {
    var result = inlinePolicies.getInlinePolicyIds(iam_data)
    var expectedResult = [
      "0e1bd3995cfe6cfbbac133f1406839e6b415e5b5a412cd148ac78071d82e5b1b",
      "9dfb8b36ce6c68a741355e7a2ab5ee62a47755f8f25d68e4fa6f87dabc036986",
      "aad4a5d1e0cd67fb99c658e1d326f16afd2f6857804f6ffd547c9c13ef508540",
      "98f5220d4d4a19fe8da59c7a2a8c2f972303a0b670cf1c3f31cad06159a5742e",
      "4331c4e6419d4ca3e11864e79a062881a78bc46804514465a7fdcb9f3471bf50",
      "4d5d2bf1baaf66fd24b21397410fd0eb30ab5758d69fc365b1862dd9a5be5eb8"
    ]
    chai.assert(result != null);
    chai.assert.deepStrictEqual(result, expectedResult)
    console.log(`Inline Policy IDs: ${JSON.stringify(result)}`);
});

it("inlinePolicies.getPrincipalTypeLeveragingInlinePolicy: should get a list of groups that leverage this inline policy", function () {
    var result = inlinePolicies.getPrincipalTypeLeveragingInlinePolicy(iam_data, "0e1bd3995cfe6cfbbac133f1406839e6b415e5b5a412cd148ac78071d82e5b1b", "Group")
    var expectedResult = ["admin"]

    chai.assert(result != null);
    chai.assert.deepStrictEqual(result, expectedResult)
    console.log(`Groups leveraging the InlinePolicyForAdminGroup inline policy: ${JSON.stringify(result)}`);
});

it("inlinePolicies.getPrincipalTypeLeveragingInlinePolicy: should get a list of USERS that leverage this inline policy", function () {
    var result = inlinePolicies.getPrincipalTypeLeveragingInlinePolicy(iam_data, "4d5d2bf1baaf66fd24b21397410fd0eb30ab5758d69fc365b1862dd9a5be5eb8", "User")
    var expectedResult = ["userwithlotsofpermissions"]
    chai.assert(result != null);
    chai.assert.deepStrictEqual(result, expectedResult)
    console.log(`Users leveraging the InsecureUserPolicy inline policy: ${JSON.stringify(result)}`);
});

it("inlinePolicies.getRolesLeveragingInlinePolicy: should return list of ROLES leveraging Inline policy", function () {
    var result = inlinePolicies.getRolesLeveragingInlinePolicy(iam_data, "aad4a5d1e0cd67fb99c658e1d326f16afd2f6857804f6ffd547c9c13ef508540");
    var expectedResult = ["MyRole"]
    chai.assert(result != null);
    chai.assert.deepStrictEqual(result, expectedResult)
    console.log(`List of roles leveraging the inline policy: ${JSON.stringify(result)}`);
});

it("inlinePolicies.inlinePolicyAssumableByComputeService: should tell us if an INLINE policy is leveraged by a role that can be run by a compute service", function() {
    var result = inlinePolicies.inlinePolicyAssumableByComputeService(iam_data, "98f5220d4d4a19fe8da59c7a2a8c2f972303a0b670cf1c3f31cad06159a5742e")
    var expectedResult = ["ec2"]
    chai.assert(result != null);
    console.log(`The role called MyOtherRole allows the use of the EC2 service: ${JSON.stringify(result)}`);
    chai.assert.deepStrictEqual(result, expectedResult, "lists do not match")
});

it("inlinePolicies.getInlinePolicyIds: should give us the object to feed into the table", function() {
    let inlinePolicyIds = inlinePolicies.getInlinePolicyIds(iam_data)
    var result = inlinePolicies.getInlinePolicyItems(iam_data, inlinePolicyIds)
    chai.assert(result != null);
    console.log(`Result: ${JSON.stringify(result.length)}`);
    console.log(`Result: ${JSON.stringify(result)}`);
    chai.assert(result.length > 5, "The results dictionary is not as large as expected")
});

it("getInlinePolicyIds.getInlinePolicyNameMapping: should give us the object to feed into the table for customers", function() {
    var result = inlinePolicies.getInlinePolicyNameMapping(iam_data)
    chai.assert(result != null);
    console.log(`Result: ${JSON.stringify(result.length)}`);
    console.log(`Result: ${JSON.stringify(result)}`);
    chai.assert(result.length > 1, "The results dictionary is not as large as expected")
});
