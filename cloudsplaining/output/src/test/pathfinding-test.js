var pathfinding = require('../util/pathfinding')
let mocha = require('mocha');
let assert;
before(async () => { ({ assert } = await import('chai')); });
let it = mocha.it;

it("pathfinding.pathfindingUrl: returns the pathfinding.cloud path URL for a mapped method", function () {
    assert.strictEqual(
        pathfinding.pathfindingUrl("CreateAccessKey"),
        "https://pathfinding.cloud/paths/iam-002"
    );
    assert.strictEqual(
        pathfinding.pathfindingUrl("PassExistingRoleToCloudFormation"),
        "https://pathfinding.cloud/paths/cloudformation-001"
    );
    assert.strictEqual(
        pathfinding.pathfindingUrl("CreateEC2WithExistingIP"),
        "https://pathfinding.cloud/paths/ec2-001"
    );
});

it("pathfinding.pathfindingUrl: returns null for a method with no pathfinding.cloud path", function () {
    // SetExistingDefaultPolicyVersion has no corresponding pathfinding.cloud path.
    assert.strictEqual(pathfinding.pathfindingUrl("SetExistingDefaultPolicyVersion"), null);
});

it("pathfinding.pathfindingUrl: returns null for an unknown method name", function () {
    assert.strictEqual(pathfinding.pathfindingUrl("NotARealMethod"), null);
});

it("pathfinding.pathfindingUrl: every mapped URL points at pathfinding.cloud/paths/", function () {
    Object.values(pathfinding.paths).forEach(function (url) {
        if (url !== null) {
            assert.match(url, /^https:\/\/pathfinding\.cloud\/paths\/[a-z0-9-]+$/);
        }
    });
});
