'use strict';

const policyViolations = (policies) => {
    let [privEsc, dataExfil, resExposure, infraMod, credExposure] = Array(5).fill(0);

    Object.keys(policies).forEach((policyId) => {
        if (policies[policyId]["PrivilegeEscalation"].length > 0){
            privEsc += 1
        }
        if (policies[policyId]["DataExfiltration"].length > 0){
            dataExfil += 1
        }
        if (policies[policyId]["ResourceExposure"].length > 0){
            resExposure += 1
        }
        if (policies[policyId]["InfrastructureModification"].length > 0){
            infraMod += 1
        }
        if (policies[policyId]["CredentialsExposure"].length > 0){
            credExposure += 1
        }
    })

    return {
        "PrivilegeEscalation": privEsc,
        "DataExfiltration": dataExfil,
        "ResourceExposure": resExposure,
        "CredentialsExposure": credExposure,
        "InfrastructureModification": infraMod,
    }
}

function addSpacesInPascalCaseString(string) {
    // "DataExfiltration" => "Data Exfiltration"
    string = string.replace(/([a-z])([A-Z])/g, '$1 $2');
    // console.log(string)
    string = string.replace(/([A-Z])([A-Z][a-z])/g, '$1 $2')
    // console.log(string)
    return string;
}

function convertStringToSnakeCase(string) {
    const toSnakeCase = str =>
    str &&
    str.match(/[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+/g)
        .map(x => x.toLowerCase())
        .join('_');
    return toSnakeCase(string)
}

function convertStringToKebabCase(string) {
    const toKebabCase = str =>
    str &&
    str.match(/[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+/g)
        .map(x => x.toLowerCase())
        .join('-');
    return toKebabCase(string)
}

function convertStringToSpaceCase(string) {
    const toSpaceCase = str =>
    str &&
    str.match(/[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+/g)
        .map(x => x.charAt(0).toUpperCase() + x.slice(1))
        .join(' ');
    return toSpaceCase(string)
}

function removeDuplicatesFromArray(someArray) {
    let uniqueArray = [];
    someArray.forEach((c) => {
        if (!uniqueArray.includes(c)) {
            uniqueArray.push(c);
        }
    });
    return uniqueArray;
}

function compareValues(key, order = 'asc') {
    // https://www.sitepoint.com/sort-an-array-of-objects-in-javascript/
  return function innerSort(a, b) {
      // eslint-disable-next-line no-prototype-builtins
    if (!a.hasOwnProperty(key) || !b.hasOwnProperty(key)) {
      // property doesn't exist on either object
      return 0;
    }

    const varA = (typeof a[key] === 'string')
      ? a[key].toUpperCase() : a[key];
    const varB = (typeof b[key] === 'string')
      ? b[key].toUpperCase() : b[key];

    let comparison = 0;
    if (varA > varB) {
      comparison = 1;
    } else if (varA < varB) {
      comparison = -1;
    }
    return (
      (order === 'desc') ? (comparison * -1) : comparison
    );
  };
}

exports.policyViolations = policyViolations;
exports.addSpacesInPascalCaseString = addSpacesInPascalCaseString;
exports.compareValues = compareValues;
exports.removeDuplicatesFromArray = removeDuplicatesFromArray;
exports.convertStringToSnakeCase = convertStringToSnakeCase;
exports.convertStringToKebabCase = convertStringToKebabCase;
exports.convertStringToSpaceCase = convertStringToSpaceCase;
