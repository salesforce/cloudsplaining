const managedPolicies = require('../util/managed-policies');
var sampleData = require('../sampleData');
let mocha = require('mocha');
let chai = require('chai');
let it = mocha.it;
let iam_data = sampleData.sample_iam_data;

it("managedPolicies.getManagedPolicyDocument: should return Managed policy document object", function() {
    var result = managedPolicies.getManagedPolicyDocument(iam_data, "Customer", "NotYourPolicy");
    var expectedResult = {"Version":"2012-10-17","Statement":[{"Sid":"VisualEditor0","Effect":"Allow","Action":["s3:PutObject","s3:PutObjectAcl"],"Resource":["arn:aws:s3:::mybucket/*","arn:aws:s3:::mybucket"]}]};
    chai.assert(result != null);
    chai.assert.deepStrictEqual(result, expectedResult);
    console.log(`Managed Policy Document: ${JSON.stringify(result)}`);
});

it("managedPolicies.getRolesLeveragingManagedPolicy: should return list of roles leveraging Managed policy", function() {
    var result = managedPolicies.getRolesLeveragingManagedPolicy(iam_data, "AWS", "ANPAI6E2CYYMI4XI7AA5K");
    var expectedResult = ["MyRole","MyOtherRole"]
    chai.assert(result != null);
    chai.assert.deepStrictEqual(result, expectedResult)
    console.log(`Roles leveraging the managed policy ANPAI6E2CYYMI4XI7AA5K: ${JSON.stringify(result)}`);
});

it("managedPolicies.getManagedPolicyFindings: should return Managed policy findings for PrivilegeEscalation", function () {
    var result = managedPolicies.getManagedPolicyFindings(iam_data, "Customer", "InsecurePolicy", "PrivilegeEscalation");
    var expectedResult = []
    chai.assert(result != null);
    chai.assert.deepStrictEqual(result, expectedResult)
    console.log(`PrivilegeEscalation findings: ${JSON.stringify(result)}`);
});

it("managedPolicies.getManagedPolicyFindings: should return Managed policy findings for ResourceExposure", function () {
    var result = managedPolicies.getManagedPolicyFindings(iam_data, "Customer", "InsecurePolicy", "ResourceExposure");
    var expectedResult = [
        "s3:PutObjectAcl"
    ]
    chai.assert(result != null);
    chai.assert.deepStrictEqual(result, expectedResult)
    console.log(`ResourceExposure findings: ${JSON.stringify(result)}`);
});

it("managedPolicies.getManagedPolicyIds: should print out all managed Policy IDs", function () {
    var result = managedPolicies.getManagedPolicyIds(iam_data, "AWS")
    var expectedResult = ["ANPAI4UIINUVGB5SEC57G","ANPAI3R4QMOG6Q5A4VWVG","ANPAI3VAJF5ZCRZ7MCQE6","ANPAI4VCZ3XPIZLQ5NZV2","ANPAI65L554VRJ33ECQS6","ANPAI6E2CYYMI4XI7AA5K","ANPAI7XKCFMBPM3QQRRVQ","ANPAIFIR6V6BVTRAHWINE","ANPAIICZJNOJN36GTG6CM","ANPAIKEABORKUXN6DEAZU","ANPAILL3HVNFSB6DCOWYQ","ANPAIMHWGGSRHLOQUICJQ","ANPAINAW5ANUWTH3R4ANI","ANPAIONKN3TJZUKXCHXWC","ANPAIQH6ROMVVECFVRJPK","ANPAIQNUJTQYDRJPC3BNK","ANPAIQRXRDRGJUA33ELIO","ANPAIWMBCKSKIEE64ZLYK","ANPAIX2T3QCXHR2OGGCTO","ANPAIZTJ4DXE7G6AGAE6M","ANPAJ2P4NXCHAT7NDPNR4","ANPAJ7W6266ELXF5MISDS","ANPAJBWPGNOVKZD3JI2P2","ANPAJH4QJ2WMHBOB47BUE","ANPAJKSO7NDY4T57MWDSQ","ANPAJLIB4VSBVO47ZSBB6","ANPAJNPP7PPPPMJRV2SA4","ANPAJS2PBJSYV2EZW3MIQ","ANPAJWVDLG5RPST6PHQ3A","ANPAJYRXTHIB4FOVS3ZXS","ANPAZKAPJZG4OV6AFDA5J"]
    chai.assert(result != null);
    chai.assert.deepStrictEqual(result, expectedResult)
    console.log(`Managed Policy IDs: ${JSON.stringify(result)}`);
});

// it("managedPolicies.managedPolicyManagedBy: should identify AWS managed vs customer managed policies", function() {
//     var result = managedPolicies.managedPolicyManagedBy(iam_data, "ANPAI4UIINUVGB5SEC57G")
//     var expectedResult = "AWS"
//     chai.assert(result != null);
//     chai.assert.strictEqual(result, expectedResult)
//     console.log(`Managed by: ${JSON.stringify(result)}`);
// });
//
// it("managedPolicies.managedPolicyManagedBy: should identify customer managed policies", function() {
//     var result = managedPolicies.managedPolicyManagedBy(iam_data, "NotYourPolicy")
//     var expectedResult = "Customer"
//     chai.assert(result != null);
//     chai.assert.strictEqual(result, expectedResult)
//     console.log(`Managed by: ${JSON.stringify(result)}`);
// });

it("managedPolicies.getServicesAffectedByManagedPolicy: should identify list of services affected by the policy findings with no duplicates", function() {
    var result = managedPolicies.getServicesAffectedByManagedPolicy(iam_data, "AWS", "ANPAI6E2CYYMI4XI7AA5K")
    var expectedResult = [
      "cloudwatch",
      "cognito-sync",
      "dynamodb",
      "events",
      "iam",
      "iot",
      "kinesis",
      "lambda",
      "logs",
      "s3",
      "sns",
      "sqs"
    ]
    chai.assert(result != null);
    chai.assert.deepStrictEqual(result, expectedResult, "lists of services used do not match")
    console.log(`Services affected: ${JSON.stringify(result)}`);
});

it("managedPolicies.getUsersLeveragingManagedPolicy: should identify Users who have the managed policy attached", function() {
    var result = managedPolicies.getUsersLeveragingManagedPolicy(iam_data, "AWS", "ANPAI4VCZ3XPIZLQ5NZV2")
    var expectedResult = ["obama"]
    chai.assert(result != null);
    chai.assert.deepStrictEqual(result, expectedResult)
    console.log(`Users leveraging the managed policy AWSCodeCommitFullAccess should equal obama: ${JSON.stringify(result)}`);
});

it("managedPolicies.getGroupsLeveragingManagedPolicy: should identify Groups who have the managed policy attached", function() {
    var result = managedPolicies.getGroupsLeveragingManagedPolicy(iam_data, "AWS", "ANPAI6E2CYYMI4XI7AA5K")
    var expectedResult = ["admin"]
    chai.assert(result != null);
    console.log(`Groups leveraging the managed policy AWSLambdaFullAccess should equal admin: ${JSON.stringify(result)}`);
    chai.assert.deepStrictEqual(result, expectedResult, "lists do not match")
});

it("managedPolicies.managedPolicyAssumableByComputeService: should tell us if a policy is leveraged by a role that can be run by a compute service", function() {
    var result = managedPolicies.managedPolicyAssumableByComputeService(iam_data, "AWS", "ANPAI6E2CYYMI4XI7AA5K")
    var expectedResult = ["lambda", "ec2"]
    chai.assert(result != null);
    console.log(`The role called MyOtherRole allows the use of the Lambda and EC2 service: ${JSON.stringify(result)}`);
    chai.assert.deepStrictEqual(result, expectedResult, "lists do not match")
});

it("managedPolicies.getManagedPolicyItems: should give us the object to feed into the table", function() {
    let managedPolicyIds = managedPolicies.getManagedPolicyIds(iam_data, "AWS")
    var result = managedPolicies.getManagedPolicyItems(iam_data, "AWS", managedPolicyIds)
    chai.assert(result != null);
    console.log(`Result: ${JSON.stringify(result.length)}`);
    console.log(`Result: ${JSON.stringify(result)}`);
    chai.assert(result.length > 30, "The results dictionary is not as large as expected")
});

it("managedPolicies.getManagedPolicyItems: should give us the object to feed into the table for customers", function() {
    let managedPolicyIds = managedPolicies.getManagedPolicyIds(iam_data, "Customer")
    var result = managedPolicies.getManagedPolicyItems(iam_data, "Customer", managedPolicyIds)
    chai.assert(result != null);
    console.log(`Result: ${JSON.stringify(result.length)}`);
    console.log(`Result: ${JSON.stringify(result)}`);
    chai.assert(result.length > 1, "The results dictionary is not as large as expected")
});

it("managedPolicies.getManagedPolicyNameMapping: should give us the object to feed into the table for customers", function() {
    var result = managedPolicies.getManagedPolicyNameMapping(iam_data, "AWS")
    chai.assert(result != null);
    console.log(`Result: ${JSON.stringify(result.length)}`);
    console.log(`Result: ${JSON.stringify(result)}`);
    chai.assert(result.length > 1, "The results dictionary is not as large as expected")
});
