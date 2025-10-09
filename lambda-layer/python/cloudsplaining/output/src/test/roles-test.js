// var expect = require('chai').expect;
var roles = require('../util/roles');
var sampleData = require('../sampleData');
let mocha = require('mocha');
let chai = require('chai');
let it = mocha.it;
let iam_data = sampleData.sample_iam_data;


it("roles.getTrustPolicyDocumentForRole: should return Trust Policy Document for role", function () {
    var result = roles.getTrustPolicyDocumentForRole(iam_data, "MyRole");
    var expectedResult = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "ssm.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    };
    chai.assert(result != null);
    chai.assert(result, expectedResult);
    console.log(`Trust Policy: ${JSON.stringify(result)}`)
});

it("roles.trustPolicyAssumableByComputeService: should return empty list to show that no compute services can assume this role", function () {
    var assumeRolePolicyDocument = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "ssm.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    };
    var result = roles.trustPolicyAssumableByComputeService(assumeRolePolicyDocument);
    var expectedResult = []
    chai.assert(result != null);
    chai.assert(result, expectedResult);
    console.log(`This should be empty: ${result}`)
});

it("roles.trustPolicyAssumableByComputeService: should return list of compute services to show which compute services can assume this role", function () {
    var assumeRolePolicyDocument = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "ec2.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    };
    var result = roles.trustPolicyAssumableByComputeService(assumeRolePolicyDocument);
    var expectedResult = ["ec2"]
    chai.assert(result != null);
    chai.assert(result, expectedResult);
    console.log(`This should be ec2: ${result}`)
});
