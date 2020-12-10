const groups = require('../util/groups')
const sampleData = require('../sampleData')

let mocha = require('mocha');
let chai = require('chai');
let it = mocha.it;
let iam_data = sampleData.sample_iam_data;


it("groups.getGroupNames: should return list of group names", function () {
    const result = groups.getGroupNames(iam_data);
    const expectedResult = Object.keys(iam_data.groups);
    chai.assert(result != null);
    chai.assert.deepEqual(result, expectedResult);
    console.log(`Should be ["admin", "biden"]: ${JSON.stringify(result)}`);
});

it("groups.getGroupMembers: should return list of users that are a member of this group", function () {
    const result = groups.getGroupMembers(iam_data, "admin");
    const expectedResult = [
        {
            "user_id": "obama",
            "user_name": "obama"
        },
        {
            "user_id": "ASIAZZUSERZZPLACEHOLDER",
            "user_name": "userwithlotsofpermissions"
        }
    ];
    chai.assert(result != null);
    chai.assert.deepEqual(result, expectedResult)
    console.log(`Should be ["obama", "userwithlotsofpermissions"] : ${JSON.stringify(result)}`);
});

it("groups.getGroupMembers: should return list of users that are a member of this group", function () {
    const result = groups.getGroupMembers(iam_data, "admin");
    const expectedResult = [
        {
            user_id: "obama",
            user_name: "obama"
        },
        {
            user_id: "ASIAZZUSERZZPLACEHOLDER",
            user_name: "userwithlotsofpermissions"
        }
    ];
    chai.assert(result != null);
    chai.assert.deepEqual(result, expectedResult)
    console.log(`Should be array of objects for the user names "obama", "userwithlotsofpermissions"] : ${JSON.stringify(result)}`);
});

it("groups.getGroupMemberships: should return list users that are a member of given group", function () {
    const result = groups.getGroupMemberships(iam_data, "ASIAZZUSERZZPLACEHOLDER");
    const expectedResult = {
        "group_id": "admin",
        "group_name": "admin"
    };
    chai.assert(result != null);
    chai.assert.lengthOf(result, 1)
    chai.assert.deepInclude(result, expectedResult)
    console.log(`Should be array of objects for the user "userwithlotsofpermissions"] : ${JSON.stringify(result)}`);
});
