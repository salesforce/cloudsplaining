var taskTable = require('../util/task-table')
var sampleData = require('../sampleData');
let mocha = require('mocha');
let assert;
before(async () => { ({ assert } = await import('chai')); });
let it = mocha.it;
let iam_data = sampleData.sample_iam_data;

it("taskTable.getTaskTableManagedPolicyItems: should give us the object to feed into the task table for managed policies", function() {
    var result = taskTable.getTaskTableMapping(iam_data, "Customer")
    assert(result != null);
    console.log(`Result: ${JSON.stringify(result.length)}`);
    // console.log(`Result: ${JSON.stringify(result, undefined, 4)}`);
    // console.log(`Result: ${JSON.stringify(result)}`);
    assert(result.length === 2, "The object should have a size of 3")
});
//
// it("taskTable.getTaskTableMapping: should give us the object to feed into the task table for managed policies", function() {
//     var result = taskTable.getTaskTableMapping(iam_data, "AWS")
//     assert(result != null);
//     console.log(`Result: ${JSON.stringify(result.length)}`);
//     console.log(`Result: ${JSON.stringify(result)}`);
//     assert(result.length > 1, "The results dictionary is not as large as expected")
// });
