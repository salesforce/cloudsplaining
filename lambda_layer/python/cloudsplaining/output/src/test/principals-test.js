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
            "ffd2b5250e18691dbd9f0fb8b36640ec574867835837f17d39f859c3193fb3f2": "InlinePolicyForAdminGroup"
        },
        "path": "/",
        "customer_managed_policies": {
            "NotYourPolicy": "NotYourPolicy"
        },
        "is_excluded": false,
        "name": "admin",
        "aws_managed_policies": {
            "ANPAI6E2CYYMI4XI7AA5K": "AWSLambdaFullAccess",
        }
    }
    chai.assert.deepStrictEqual(result, expectedResult);
    console.log(`Should return all metadata under the group admin: ${JSON.stringify(result)}`);
});

it("principals.getPrincipalIds: should return a list of principal IDs for a given principal type", function () {
    var result = principals.getPrincipalIds(iam_data, "User");
    var expectedResult = ["ASIAZZUSERZZPLACEHOLDER", "obama"]
    chai.assert.deepStrictEqual(result, expectedResult);
    console.log(`Should return the list of users ["obama", "ASIAZZUSERZZPLACEHOLDER"]: ${JSON.stringify(result)}`);
});

it("principals.getPrincipalNames: should return a list of principal names for a given principal type", function () {
    var result = principals.getPrincipalNames(iam_data, "User");
    var expectedResult = ["obama", "userwithlotsofpermissions"]
    chai.assert.deepStrictEqual(result, expectedResult);
    console.log(`Should return the list of users ["obama", "userwithlotsofpermissions"]: ${JSON.stringify(result)}`);
});


it("principals.getPrincipalPolicies: should return Inline policies with principal", function () {
    var result = principals.getPrincipalPolicies(iam_data, "admin", "Group", "Inline");
    var expectedResult = [ 'ffd2b5250e18691dbd9f0fb8b36640ec574867835837f17d39f859c3193fb3f2' ]
    chai.assert.deepStrictEqual(result, expectedResult);
    console.log(`Should return inline policy ID [ '0e1bd3995cfe6cfbbac133f1406839e6b415e5b5a412cd148ac78071d82e5b1b' ] associated with group admin: ${JSON.stringify(result)}`);
});


it("principals.getRiskAssociatedWithPrincipal: should return risks associated with principal", function () {
    let result = principals.getRiskAssociatedWithPrincipal(iam_data, "admin", "Group", "ResourceExposure");
    chai.assert(result != null);
    console.log(`ResourceExposure risks associated with the group admin should be greater than 20: ${JSON.stringify(result.length)}`);
    chai.assert.isAtLeast(result.length, 20, `ResourceExposure risks associated with the group admin should be greater than 20: ${JSON.stringify(result.length)}`)
    // chai.assert.deepStrictEqual(result, expectedResult);
});


it("principals.getRiskAssociatedWithPrincipal: should return risks associated with principal", function () {
    let result = principals.getRiskAssociatedWithPrincipal(iam_data, "admin", "Group", "ResourceExposure");
    chai.assert(result != null);
    console.log(`ResourceExposure risks associated with the group admin should be greater than 20: ${JSON.stringify(result.length)}`);
    chai.assert.isAtLeast(result.length, 20, `ResourceExposure risks associated with the group admin should be greater than 20: ${JSON.stringify(result.length)}`)
    // chai.assert.deepStrictEqual(result, expectedResult);
});
