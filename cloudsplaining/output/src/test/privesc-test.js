let mocha = require('mocha');
let chai = require('chai');
let it = mocha.it;

let privesc_methods = require('../util/privilege-escalation-methods')

it("privesc_methods.getPrivilegeEscalationType: should return the action combinations and the description", function () {
    let result = privesc_methods.getPrivilegeEscalationType("CreateAccessKey");
    // let expectedResult = ["admin"];
    console.log(JSON.stringify(result["actions"]))
    console.log(JSON.stringify(result))
    chai.assert(Object.prototype.hasOwnProperty.call(result, "actions"))
    chai.assert(Object.prototype.hasOwnProperty.call(result, "description"))
    chai.assert(result["actions"][0] === "iam:createaccesskey");
    // chai.assert(result, expectedResult);
    // console.log(`Should be only ["admin"]: ${JSON.stringify(result)}`);
});
