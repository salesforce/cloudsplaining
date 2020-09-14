var principals = require('../util/principals')

var sampleData = require('../sampleData');
let mocha = require('mocha');
let chai = require('chai');
let it = mocha.it;
let iam_data = sampleData.sample_iam_data;

it("principals.getPrincipalMetadata: should return principal object", function () {
    var result = principals.getPrincipalMetadata(iam_data, "admin", "Group");
    var expectedResult = {
        "arn": "arn:aws:iam::012345678901:group/admin",
        "create_date": "2017-05-15 17:33:36+00:00",
        "id": "admin",
        "inline_policies": {
            "0e1bd3995cfe6cfbbac133f1406839e6b415e5b5a412cd148ac78071d82e5b1b": "InlinePolicyForAdminGroup"
        },
        "path": "/",
        "customer_managed_policies": {
            "NotYourPolicy": "NotYourPolicy"
        },
        "aws_managed_policies": {
            "ANPAIWMBCKSKIEE64ZLYK": "AdministratorAccess",
            "ANPAI6E2CYYMI4XI7AA5K": "AWSLambdaFullAccess"
        }
    }
    chai.assert.deepStrictEqual(result, expectedResult);
    console.log(`Should return all metadata under the group admin: ${JSON.stringify(result)}`);
});

it("principals.getPrincipalNames: should return a list of principals for a given principal type", function () {
    var result = principals.getPrincipalNames(iam_data, "User");
    var expectedResult = ["obama", "userwithlotsofpermissions"]
    chai.assert.deepStrictEqual(result, expectedResult);
    console.log(`Should return the list of users ["obama", "userwithlotsofpermissions"]: ${JSON.stringify(result)}`);
});

it("principals.getPrincipalPolicies: should return Inline policies with principal", function () {
    var result = principals.getPrincipalPolicies(iam_data, "admin", "Group", "Inline");
    var expectedResult = [ '0e1bd3995cfe6cfbbac133f1406839e6b415e5b5a412cd148ac78071d82e5b1b' ]
    chai.assert.deepStrictEqual(result, expectedResult);
    console.log(`Should return inline policy ID [ '0e1bd3995cfe6cfbbac133f1406839e6b415e5b5a412cd148ac78071d82e5b1b' ] associated with group admin: ${JSON.stringify(result)}`);
});


it("principals.getRiskAssociatedWithPrincipal: should return risks associated with principal", function () {
    var result = principals.getRiskAssociatedWithPrincipal(iam_data, "admin", "Group", "ResourceExposure");
    chai.assert(result != null);
    console.log(`ResourceExposure risks associated with the group admin should be greater than 290: ${JSON.stringify(result.length)}`);
    chai.assert(result.length > 290)
    // chai.assert.deepStrictEqual(result, expectedResult);
    console.log(`ResourceExposure risks associated with the group admin should be greater than 290: ${JSON.stringify(result.length)}`);
});


it("principals.getRiskAssociatedWithPrincipal: should return risks associated with principal", function () {
    var result = principals.getRiskAssociatedWithPrincipal(iam_data, "admin", "Group", "ResourceExposure");
    chai.assert(result != null);
    console.log(`ResourceExposure risks associated with the group admin should be greater than 290: ${JSON.stringify(result.length)}`);
    chai.assert(result.length > 290)
    // chai.assert.deepStrictEqual(result, expectedResult);
    console.log(`ResourceExposure risks associated with the group admin should be greater than 290: ${JSON.stringify(result.length)}`);
});
