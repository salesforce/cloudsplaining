var inlinePolicies = require('../util/inline-policies')
var sampleData = require('../sampleData');
let mocha = require('mocha');
let chai = require('chai');
let it = mocha.it;
let iam_data = sampleData.sample_iam_data;

it("inlinePolicies.getInlinePolicyDocument: should return Inline policy document object", function () {
    var result = inlinePolicies.getInlinePolicyDocument(iam_data, "e8bca32ff7d1f7990d71c64d95a04b7caa5aad5791f06f69db59653228c6853d");
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
    var result = inlinePolicies.getServicesAffectedByInlinePolicy(iam_data, "e8bca32ff7d1f7990d71c64d95a04b7caa5aad5791f06f69db59653228c6853d")
    var expectedResult = [
        "s3",
    ]
    chai.assert(result != null);
    chai.assert.deepStrictEqual(result, expectedResult, "lists of services used do not match")
    console.log(`Services affected: ${JSON.stringify(result)}`);
});


it("inlinePolicies.getInlinePolicyFindings: should return Inline policy findings for PrivilegeEscalation", function () {
    var result = inlinePolicies.getInlinePolicyFindings(iam_data, "d09fe3603cd65058b6e2d9817cf37093e83e98318a56ce1e29c8491ac989e57e", "PrivilegeEscalation");
    var expectedResult = [
                {
                    "type": "CreateAccessKey",
                    "actions": [
                        "iam:createaccesskey"
                    ]
                }
            ]
    chai.assert(result != null);
    chai.assert.deepStrictEqual(result, expectedResult)
    console.log(`PrivilegeEscalation findings: ${JSON.stringify(result)}`);
});

it("inlinePolicies.getInlinePolicyFindings: should return Inline policy findings for ResourceExposure", function () {
    var result = inlinePolicies.getInlinePolicyFindings(iam_data, "0568550cb147d2434f6c04641e921f18fe1b7b1fd0b5af5acf514d33d204faca", "ResourceExposure");
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
      "ffd2b5250e18691dbd9f0fb8b36640ec574867835837f17d39f859c3193fb3f2",
      "e8bca32ff7d1f7990d71c64d95a04b7caa5aad5791f06f69db59653228c6853d",
      "0568550cb147d2434f6c04641e921f18fe1b7b1fd0b5af5acf514d33d204faca",
      "d09fe3603cd65058b6e2d9817cf37093e83e98318a56ce1e29c8491ac989e57e",
      "354d81e1788639707f707738fb4c630cb7c5d23614cc467ff9a469a670049e3f"

    ]
    chai.assert(result != null);
    chai.assert.deepStrictEqual(result, expectedResult)
    console.log(`Inline Policy IDs: ${JSON.stringify(result)}`);
});

it("inlinePolicies.getPrincipalTypeLeveragingInlinePolicy: should get a list of groups that leverage this inline policy", function () {
    var result = inlinePolicies.getPrincipalTypeLeveragingInlinePolicy(iam_data, "ffd2b5250e18691dbd9f0fb8b36640ec574867835837f17d39f859c3193fb3f2", "Group")
    var expectedResult = ["admin"]
    chai.assert(result != null);
    chai.assert.deepStrictEqual(result, expectedResult)
    console.log(`Groups leveraging the InlinePolicyForAdminGroup inline policy: ${JSON.stringify(result)}`);
});

it("inlinePolicies.getPrincipalTypeLeveragingInlinePolicy: should get a list of USERS that leverage this inline policy", function () {
    var result = inlinePolicies.getPrincipalTypeLeveragingInlinePolicy(iam_data, "354d81e1788639707f707738fb4c630cb7c5d23614cc467ff9a469a670049e3f", "User")
    var expectedResult = ["userwithlotsofpermissions"]
    chai.assert(result != null);
    chai.assert.deepStrictEqual(result, expectedResult)
    console.log(`User names leveraging the InsecureUserPolicy inline policy: ${JSON.stringify(result)}`);
});

it("inlinePolicies.getRolesLeveragingInlinePolicy: should return list of ROLES leveraging Inline policy", function () {
    var result = inlinePolicies.getRolesLeveragingInlinePolicy(iam_data, "0568550cb147d2434f6c04641e921f18fe1b7b1fd0b5af5acf514d33d204faca");
    var expectedResult = ["MyRole", "MyOtherRole"]
    chai.assert(result != null);
    chai.assert.deepStrictEqual(result, expectedResult)
    console.log(`List of roles leveraging the inline policy: ${JSON.stringify(result)}`);
});

it("inlinePolicies.inlinePolicyAssumableByComputeService: should tell us if an INLINE policy is leveraged by a role that can be run by a compute service", function() {
    var result = inlinePolicies.inlinePolicyAssumableByComputeService(iam_data, "0568550cb147d2434f6c04641e921f18fe1b7b1fd0b5af5acf514d33d204faca")
    var expectedResult = ["lambda", "ec2"]
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
    chai.assert(result.length === 5, "The results dictionary is not as large as expected")
});

it("getInlinePolicyIds.getInlinePolicyNameMapping: should give us the object to feed into the table for customers", function() {
    var result = inlinePolicies.getInlinePolicyNameMapping(iam_data)
    chai.assert(result != null);
    console.log(`Result: ${JSON.stringify(result.length)}`);
    console.log(`Result: ${JSON.stringify(result)}`);
    chai.assert(result.length > 1, "The results dictionary is not as large as expected")
});
