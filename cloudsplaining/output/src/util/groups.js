'use strict';

function getGroupNames(iam_data) {
    return Object.keys(iam_data["groups"]);
}

function getGroupMembers(iam_data, groupId) {
    // Look through users
    let userObjects;
    userObjects = Object.keys(iam_data["users"]);
    const members = [];
    for (let i = 0; i < userObjects.length; i++) {
        let userId = userObjects[i];
        let groupMemberships = iam_data["users"][userId]["groups"];
        if (Object.prototype.hasOwnProperty.call(groupMemberships, groupId)) {
            members.push(userId);
        }
    }
    return members;
}

exports.getGroupNames = getGroupNames;
exports.getGroupMembers = getGroupMembers;
