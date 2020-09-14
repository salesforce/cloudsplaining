'use strict';

function getGroupNames(iam_data) {
    return Object.keys(iam_data["groups"]);
}

function getGroupMembers(iam_data, groupName) {
    // Look through users
    let userObjects;
    userObjects = Object.keys(iam_data["users"]);
    const members = [];
    for (let i = 0; i < userObjects.length; i++) {
        let userName = userObjects[i];
        let groupMemberships = iam_data["users"][userName]["groups"];
        if (Object.prototype.hasOwnProperty.call(groupMemberships, groupName)) {
            members.push(userName);
        }
    }
    return members;
}

exports.getGroupNames = getGroupNames;
exports.getGroupMembers = getGroupMembers;