// var expect = require('chai').expect;
var groups = require('../util/groups')
var sampleData = require('../sampleData')

let mocha = require('mocha');
let chai = require('chai');
let it = mocha.it;
let iam_data = sampleData.sample_iam_data;


it("groups.getGroupNames: should return list of group names", function () {
    var result = groups.getGroupNames(iam_data);
    var expectedResult = ["admin"];
    chai.assert(result != null);
    chai.assert(result, expectedResult);
    console.log(`Should be only ["admin"]: ${JSON.stringify(result)}`);
});

// it("groups.getGroupMembers: should a list of users that are a member of this group", function () {
//     var result = groups.getGroupMembers(iam_data, "admin");
//     var expectedResult = ["obama", "ASIAZZUSERZZPLACEHOLDER"];
//     chai.assert(result != null);
//     chai.assert.deepStrictEqual(result, expectedResult)
//     console.log(`Should be ["obama", "userwithlotsofpermissions"] : ${JSON.stringify(result)}`);
// });

it("groups.getGroupMembers: should a list of users that are a member of this group", function () {
    var result = groups.getGroupMembers(iam_data, "admin");
    var expectedResult = [
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
    chai.assert.deepStrictEqual(result, expectedResult)
    console.log(`Should be array of objects for the user names "obama", "userwithlotsofpermissions"] : ${JSON.stringify(result)}`);
});

it("groups.getGroupMemberships: should a list of users that are a member of this group", function () {
    var result = groups.getGroupMemberships(iam_data, "ASIAZZUSERZZPLACEHOLDER");
    var expectedResult = [
      {
        "group_id": "admin",
        "group_name": "admin"
      }
    ];
    chai.assert(result != null);
    chai.assert.deepStrictEqual(result, expectedResult)
    console.log(`Should be array of objects for the user names "obama", "userwithlotsofpermissions"] : ${JSON.stringify(result)}`);
});
