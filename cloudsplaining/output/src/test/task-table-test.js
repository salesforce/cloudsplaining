var taskTable = require('../util/task-table')
var sampleData = require('../sampleData');
let mocha = require('mocha');
let chai = require('chai');
let it = mocha.it;
let iam_data = sampleData.sample_iam_data;

it("taskTable.getTaskTableManagedPolicyItems: should give us the object to feed into the task table for managed policies", function() {
    var result = taskTable.getTaskTableMapping(iam_data, "Customer")
    chai.assert(result != null);
    console.log(`Result: ${JSON.stringify(result.length)}`);
    // console.log(`Result: ${JSON.stringify(result, undefined, 4)}`);
    // console.log(`Result: ${JSON.stringify(result)}`);
    chai.assert(result.length === 2, "The object should have a size of 3")
});
//
// it("taskTable.getTaskTableMapping: should give us the object to feed into the task table for managed policies", function() {
//     var result = taskTable.getTaskTableMapping(iam_data, "AWS")
//     chai.assert(result != null);
//     console.log(`Result: ${JSON.stringify(result.length)}`);
//     console.log(`Result: ${JSON.stringify(result)}`);
//     chai.assert(result.length > 1, "The results dictionary is not as large as expected")
// });
