"""
Methods that execute specific queries against the SQLite database for the SERIVCES table.
This supports the policy_sentry query functionality
"""

from __future__ import annotations

from policy_sentry.shared.iam_data import iam_definition


def get_services_data() -> list[dict[str, str]]:
    return [
        {
            "prefix": service_prefix,
            "service_name": data["service_name"],
        }
        for service_prefix, data in iam_definition.items()
        if isinstance(data, dict)
    ]
