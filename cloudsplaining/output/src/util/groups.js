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
            let entry = {
                user_id: userId,
                user_name: iam_data["users"][userId]["name"]
            }
            members.push(Object.assign(entry));
        }
    }
    return members;
}

function getGroupMemberships(iam_data, userId) {
    // Look through users
    let result = [];
    let groupMembershipIds;
    groupMembershipIds = Array.from(Object.keys(iam_data["users"][userId]["groups"]));
    if (Object.keys(groupMembershipIds).length > 0) {
        // the "groups" under here are the group IDs, not the group names.
        // Let's go retrieve an object that maps the IDs to the Group names


        for (let groupId of groupMembershipIds) {
        // for (let i = 0; i < Object.keys(groupMembershipIds).length; i++) {
            if (Object.prototype.hasOwnProperty.call(iam_data["groups"], groupId)) {
                let entry = {
                    group_id: groupId.slice(),
                    group_name: iam_data["groups"][groupId]["name"].slice()
                };
                result.push(Object.assign(entry));
            }
        }
    }
    return result;
}

exports.getGroupNames = getGroupNames;
exports.getGroupMembers = getGroupMembers;
exports.getGroupMemberships = getGroupMemberships;
