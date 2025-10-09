'use strict';

function getGroupNames(iam_data) {
    return Object.keys(iam_data["groups"]);
}

/**
 * Collects members that belong to IAM Group matching given groupId
 * @param iam_data Global container with IAM report
 * @param groupId Group we are filtering against
 * @returns [{string: any}]
 */
function getGroupMembers(iam_data, groupId) {
    const userObjects = Object.keys(iam_data["users"]);

    if (!userObjects.length) {
        return [];
    }

    const members = [];

    // todo: clean this up with a nicer map/filter/reduce
    for (let i = 0; i < userObjects.length; i++) {
        let userId = userObjects[i];
        let groupMemberships = Object.values(iam_data["users"][userId]["groups"]);

        if (groupMemberships.some(group => group.id === groupId)) {
            members.push({
                user_id: userId,
                user_name: iam_data["users"][userId]["name"]
            })
        }
    }
    return members;
}

/**
 * Collects IAM Groups a user belongs to
 * @param iam_data Global container with IAM report
 * @param userId AWS unique user identifier to filtering against
 * @returns [{string: any}]
 */
function getGroupMemberships(iam_data, userId) {

    let groupMemberships = iam_data["users"][userId].groups;

    if (!groupMemberships || !Object.keys(groupMemberships).length) {
        return [];
    }

    return Object.values(groupMemberships).reduce((groups, group) => {
        return [...groups, {group_id: group.id, group_name: group.name}]
    }, [])
}

exports.getGroupNames = getGroupNames;
exports.getGroupMembers = getGroupMembers;
exports.getGroupMemberships = getGroupMemberships;
