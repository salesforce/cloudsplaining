"""Lock the two committed example fixtures together.

``utils/generate_example_iam_data.py`` writes BOTH ``utils/example-iam-data.json``
and ``cloudsplaining/output/src/sampleData.js`` from the same scan ``results``.
If only one is regenerated they silently drift apart (the frontend mocha tests
then assert against stale data). This test parses the JSON payload back out of
``sampleData.js`` and requires it to equal ``example-iam-data.json``.

Regenerate both with ``just generate-report`` if this fails.
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SAMPLE_DATA_JS = REPO_ROOT / "cloudsplaining" / "output" / "src" / "sampleData.js"
EXAMPLE_IAM_DATA = REPO_ROOT / "utils" / "example-iam-data.json"

_PREFIX = "var sample_iam_data = "
_SUFFIX_MARKER = "exports.sample_iam_data"


def _payload_from_sample_data_js() -> dict:
    text = SAMPLE_DATA_JS.read_text()
    assert text.startswith(_PREFIX), f"sampleData.js must start with {_PREFIX!r}"
    body = text[len(_PREFIX) :]
    body = body.split(_SUFFIX_MARKER)[0].rstrip()
    return json.loads(body)


def test_sample_data_js_matches_example_iam_data():
    sample_payload = _payload_from_sample_data_js()
    example_payload = json.loads(EXAMPLE_IAM_DATA.read_text())
    assert sample_payload == example_payload, (
        "sampleData.js and utils/example-iam-data.json are out of sync. "
        "Run `just generate-report` to regenerate both from examples/files/example.json."
    )
