"""
Just some text transformation functions related to our
conditions-related workarounds
"""


# Borrowed from parliament. Altered with normalization for lowercase.
def translate_condition_key_data_types(condition_str: str) -> str:
    """
    The docs use different type names, so this standardizes them.
    Example: The condition secretsmanager:RecoveryWindowInDays is listed as using a "Long"
    So return "Number"
    """
    condition_lowercase = condition_str.lower()
    if condition_lowercase in ("arn", "arn"):
        return "Arn"
    elif condition_lowercase in ("bool", "boolean"):
        return "Bool"
    elif condition_lowercase == "date":
        return "Date"
    elif condition_lowercase in ("long", "numeric"):
        return "Number"
    elif condition_lowercase in ("string", "string", "arrayofstring"):
        return "String"
    elif condition_lowercase == "ip":
        return "Ip"
    else:
        raise Exception(f"Unknown data format: {condition_lowercase}")


def get_service_from_condition_key(condition_key: str) -> str:
    """Given a condition key, return the service prefix"""
    return condition_key.split(":", 2)[0]


def get_comma_separated_condition_keys(condition_keys: str) -> str:
    """
    :param condition_keys: String containing multiple condition keys, separated by double spaces
    :return: result: String containing multiple condition keys, comma-separated
    """

    # replace the double spaces with a comma
    return condition_keys.replace("  ", ",")


def is_condition_key_match(document_key: str, some_str: str) -> bool:
    """Given a documented condition key and one from a policy, determine if they match
    Examples:
    - s3:prefix and s3:prefix obviously match
    - s3:ExistingObjectTag/<key> and s3:ExistingObjectTag/backup match
    """

    # Normalize both
    document_key = document_key.lower()
    some_str = some_str.lower()

    # Check if the document key has a pattern match in it
    if "$" in document_key:
        # Some services use a format like license-manager:ResourceTag/${TagKey}
        if some_str.startswith(document_key.split("$")[0]):
            return True
    elif "<" in document_key:
        # Some services use a format like s3:ExistingObjectTag/<key>
        if some_str.startswith(document_key.split("<")[0]):
            return True
    elif "tag-key" in document_key:  # noqa: SIM102
        # Some services use a format like secretsmanager:ResourceTag/tag-key
        if some_str.startswith(document_key.split("tag-key")[0]):
            return True

    # Just return whether they match exactly
    return document_key == some_str
