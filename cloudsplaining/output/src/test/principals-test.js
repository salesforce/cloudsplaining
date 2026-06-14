var principals = require('../util/principals')
var sampleData = require('../sampleData');
let mocha = require('mocha');
let assert;
before(async () => { ({ assert } = await import('chai')); });
let it = mocha.it;
let iam_data = sampleData.sample_iam_data;

it("principals.getPrincipalMetadata: should return principal object", function () {
    var result = principals.getPrincipalMetadata(iam_data, "aaaaaaaaabbbbbbbccccccc", "Group");
    var expectedResult = {
        "arn": "arn:aws:iam::012345678901:group/biden",
        "create_date": "2017-05-15 17:33:36+00:00",
        "id": "aaaaaaaaabbbbbbbccccccc",
        "inline_policies": {
            "e8bca32ff7d1f7990d71c64d95a04b7caa5aad5791f06f69db59653228c6853d": "InlinePolicyForBidenGroup"
        },
        "path": "/",
        "customer_managed_policies": {},
        "is_excluded": false,
        "name": "biden",
        "aws_managed_policies": {
            "ANPAI3R4QMOG6Q5A4VWVG": "AmazonRDSFullAccess"
        }
    }
    assert.deepStrictEqual(result, expectedResult);
    console.log(`Should return all metadata under the group biden: ${JSON.stringify(result)}`);
});

it("principals.getPrincipalIds: should return a list of principal IDs for a given principal type", function () {
    var result = principals.getPrincipalIds(iam_data, "User");
    // The dataset now contains many more users. Assert the known teaching IDs are present...
    var knownIds = ["ASIAZZUSERZZPLACEHOLDER", "obama", "biden"]
    assert(result != null);
    assert(result.length >= 3, `Expected at least 3 user IDs, got ${result.length}`)
    knownIds.forEach(function(id) {
      assert(result.includes(id), `Expected user ID ${id} to be present in results`)
    })
    // ...and that IDs are ordered alphabetically by their principal NAME (#238), not by the
    // opaque ID. Re-derive names in the returned order and assert they are non-decreasing,
    // mirroring getPrincipalIds' comparator (case-insensitive name, with ID fallback).
    var namesInReturnedOrder = result.map(function (id) {
        return ((iam_data["users"][id] && iam_data["users"][id].name) || id).toLowerCase();
    });
    var sortedNames = namesInReturnedOrder.slice().sort(function (a, b) {
        return a.localeCompare(b);
    });
    assert.deepStrictEqual(namesInReturnedOrder, sortedNames, "Expected user IDs to be ordered alphabetically by name");
    console.log(`User IDs ordered by name: ${JSON.stringify(result)}`);
});

it("principals.getPrincipalNames: should return a list of principal names for a given principal type", function () {
    var result = principals.getPrincipalNames(iam_data, "User");
    // The dataset now contains many more users. Assert the known teaching names are present.
    var knownNames = ["obama", "userwithlotsofpermissions", "biden"]
    assert(result != null);
    assert(result.length >= 3, `Expected at least 3 user names, got ${result.length}`)
    knownNames.forEach(function(name) {
      assert(result.includes(name), `Expected user name ${name} to be present in results`)
    })
    console.log(`User names includes teaching entities: ${JSON.stringify(result)}`);
});


it("principals.getPrincipalPolicies: should return Inline policies with principal", function () {
    var result = principals.getPrincipalPolicies(iam_data, "aaaaaaaaabbbbbbbccccccc", "Group", "Inline");
    var expectedResult = [ 'e8bca32ff7d1f7990d71c64d95a04b7caa5aad5791f06f69db59653228c6853d' ]
    assert.deepStrictEqual(result, expectedResult);
    console.log(`Should return inline policy ID e8bca32... (InlinePolicyForBidenGroup) associated with group biden: ${JSON.stringify(result)}`);
});


it("principals.getRiskAssociatedWithPrincipal: should return risks associated with principal", function () {
    // Use privesc-sre-group (AGPAS5NLFGDT46LVQ2E6N) which has 100+ ResourceExposure findings
    let result = principals.getRiskAssociatedWithPrincipal(iam_data, "AGPAS5NLFGDT46LVQ2E6N", "Group", "ResourceExposure");
    assert(result != null);
    console.log(`ResourceExposure risks associated with the privesc-sre-group should be greater than 20: ${JSON.stringify(result.length)}`);
    assert.isAtLeast(result.length, 20, `ResourceExposure risks associated with the privesc-sre-group should be greater than 20: ${JSON.stringify(result.length)}`)
    // assert.deepStrictEqual(result, expectedResult);
});


it("principals.getRiskAssociatedWithPrincipal: should return risks associated with principal", function () {
    // Use privesc-sre-group (AGPAS5NLFGDT46LVQ2E6N) which has 100+ ResourceExposure findings
    let result = principals.getRiskAssociatedWithPrincipal(iam_data, "AGPAS5NLFGDT46LVQ2E6N", "Group", "ResourceExposure");
    assert(result != null);
    console.log(`ResourceExposure risks associated with the privesc-sre-group should be greater than 20: ${JSON.stringify(result.length)}`);
    assert.isAtLeast(result.length, 20, `ResourceExposure risks associated with the privesc-sre-group should be greater than 20: ${JSON.stringify(result.length)}`)
    // assert.deepStrictEqual(result, expectedResult);
});
