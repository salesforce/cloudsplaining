"""Validate JSON/YAML formatted templates/data, such as the exclusions template and the Authorization details file."""
# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# Licensed under the BSD 3-Clause license.
# For full license text, see the LICENSE file in the repo root
# or https://opensource.org/licenses/BSD-3-Clause
import logging
from typing import Dict, List, Any

from schema import Optional, Schema, SchemaError

logger = logging.getLogger(__name__)

EXCLUSIONS_TEMPLATE_SCHEMA = Schema(
    {
        Optional("policies"): [str],
        Optional("roles"): [str],
        Optional("users"): [str],
        Optional("groups"): [str],
        Optional("exclude-actions"): [str],
        Optional("include-actions"): [str],
    }
)

AUTHORIZATION_DETAILS_SCHEMA = Schema(
    {
        "UserDetailList": [object],
        "GroupDetailList": [object],
        "RoleDetailList": [object],
        "Policies": [object],
    }
)


# pragma: no cover
def check(conf_schema: Schema, conf: Dict[str, List[Any]]) -> bool:
    """
    Validates a user-supplied JSON vs a defined schema.
    :param conf_schema: The Schema object that defines the required structure.
    :param conf: The user-supplied schema to validate against the required structure.
    """
    try:
        conf_schema.validate(conf)
        return True
    except SchemaError as schema_error:
        try:
            # workarounds for Schema's logging approach
            print(schema_error.autos[0])
            detailed_error_message = schema_error.autos[2]
            print(detailed_error_message.split(" in {'")[0])  # pragma: no cover
            # for error in schema_error.autos:
        except:  # pylint: disable=bare-except
            logger.critical(schema_error)
        return False


def check_exclusions_schema(cfg: Dict[str, List[str]]) -> bool:
    """Determine whether or not the exclusions file meets the required format"""
    result = check(EXCLUSIONS_TEMPLATE_SCHEMA, cfg)
    if result:
        return result
    else:
        raise Exception(
            "The required format of the exclusions template is incorrect. Please try again."
        )


def check_authorization_details_schema(cfg: Dict[str, List[Any]]) -> bool:
    """Determine whether or not the file meets the required format of the authorizations file"""
    result = check(AUTHORIZATION_DETAILS_SCHEMA, cfg)
    return result
