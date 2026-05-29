"""Guards the privilege-escalation -> pathfinding.cloud link mapping.

The report links each detected privilege-escalation method to its pathfinding.cloud
path via cloudsplaining/output/src/util/pathfinding-paths.json. That file must stay in
lockstep with PRIVILEGE_ESCALATION_METHODS in constants.py: every method needs an entry
(a URL, or null when no pathfinding.cloud path exists), and every URL must be well-formed.
"""

import json
import re
from pathlib import Path

from cloudsplaining.shared.constants import (
    PRIVILEGE_ESCALATION_METHODS,
    PRIVILEGE_ESCALATION_PATHFINDING_PATHS,
)

PATHFINDING_PATHS_FILE = (
    Path(__file__).parents[2] / "cloudsplaining" / "output" / "src" / "util" / "pathfinding-paths.json"
)
PATHFINDING_URL_RE = re.compile(r"^https://pathfinding\.cloud/paths/[a-z0-9-]+$")


def _load_mapping() -> dict:
    return json.loads(PATHFINDING_PATHS_FILE.read_text())


def test_every_privesc_method_has_a_mapping_entry():
    mapping = _load_mapping()
    missing = set(PRIVILEGE_ESCALATION_METHODS) - set(mapping)
    assert not missing, f"pathfinding-paths.json is missing entries for: {sorted(missing)}"


def test_mapping_has_no_unknown_methods():
    mapping = _load_mapping()
    extra = set(mapping) - set(PRIVILEGE_ESCALATION_METHODS)
    assert not extra, f"pathfinding-paths.json has entries not in PRIVILEGE_ESCALATION_METHODS: {sorted(extra)}"


def test_mapped_urls_are_well_formed():
    mapping = _load_mapping()
    for method, url in mapping.items():
        if url is not None:
            assert PATHFINDING_URL_RE.match(url), f"{method} has a malformed pathfinding URL: {url!r}"


def test_python_and_js_mappings_match():
    """constants.py (used to generate the data) and the shipped JSON (used by the Vue
    report) must be identical, so the report and the data never disagree."""
    assert PRIVILEGE_ESCALATION_PATHFINDING_PATHS == _load_mapping()
