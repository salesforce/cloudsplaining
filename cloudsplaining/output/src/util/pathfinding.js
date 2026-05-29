// Maps cloudsplaining privilege-escalation method names to their corresponding
// pathfinding.cloud path page, so the report can link each detected method to the
// canonical writeup at https://pathfinding.cloud/paths/<id>.
//
// Source of truth: pathfinding-paths.json (keys mirror PRIVILEGE_ESCALATION_METHODS
// in cloudsplaining/shared/constants.py). A method with no pathfinding.cloud path
// maps to null. See research/pathfinding-cloud/method-to-pathfinding.json for how
// each mapping was derived.
const paths = require('./pathfinding-paths.json');

function pathfindingUrl(methodType) {
    return paths[methodType] || null;
}

module.exports = {
    paths,
    pathfindingUrl,
};
