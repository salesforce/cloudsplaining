"""Tests for utils/build_example_dataset.py — the example-dataset enrichment merge.

The merge folds a teaching authorization-details fixture into the realistic
example.json so the demo report shows both. It must be deterministic and
idempotent, dedup principals by natural key, and union managed policies by Arn.
"""

from utils.build_example_dataset import merge_authorization_details


def _user(name, arn):
    return {"UserName": name, "Arn": arn}


def test_merge_appends_non_colliding_principals():
    base = {"UserDetailList": [_user("alice", "arn:user/alice")], "Policies": []}
    overlay = {"UserDetailList": [_user("bob", "arn:user/bob")], "Policies": []}

    merged = merge_authorization_details(base, overlay)

    assert {u["UserName"] for u in merged["UserDetailList"]} == {"alice", "bob"}


def test_merge_skips_principal_with_duplicate_name():
    base = {"UserDetailList": [_user("alice", "arn:a")], "Policies": []}
    overlay = {"UserDetailList": [_user("alice", "arn:DIFFERENT")], "Policies": []}

    merged = merge_authorization_details(base, overlay)

    assert len(merged["UserDetailList"]) == 1
    assert merged["UserDetailList"][0]["Arn"] == "arn:a"


def test_merge_skips_principal_with_duplicate_arn():
    base = {"RoleDetailList": [{"RoleName": "r1", "Arn": "arn:role/x"}], "Policies": []}
    overlay = {"RoleDetailList": [{"RoleName": "r2", "Arn": "arn:role/x"}], "Policies": []}

    merged = merge_authorization_details(base, overlay)

    assert len(merged["RoleDetailList"]) == 1


def test_merge_unions_policies_by_arn():
    base = {"Policies": [{"PolicyName": "P", "Arn": "arn:p1"}]}
    overlay = {"Policies": [{"PolicyName": "P", "Arn": "arn:p1"}, {"PolicyName": "Q", "Arn": "arn:p2"}]}

    merged = merge_authorization_details(base, overlay)

    assert [p["Arn"] for p in merged["Policies"]] == ["arn:p1", "arn:p2"]


def test_merge_handles_groups_and_roles():
    base = {
        "GroupDetailList": [{"GroupName": "g1", "Arn": "arn:group/g1"}],
        "RoleDetailList": [{"RoleName": "r1", "Arn": "arn:role/r1"}],
        "Policies": [],
    }
    overlay = {
        "GroupDetailList": [{"GroupName": "g2", "Arn": "arn:group/g2"}],
        "RoleDetailList": [{"RoleName": "r2", "Arn": "arn:role/r2"}],
        "Policies": [],
    }

    merged = merge_authorization_details(base, overlay)

    assert {g["GroupName"] for g in merged["GroupDetailList"]} == {"g1", "g2"}
    assert {r["RoleName"] for r in merged["RoleDetailList"]} == {"r1", "r2"}


def test_merge_is_idempotent():
    base = {"UserDetailList": [_user("a", "arn:a")], "Policies": [{"Arn": "arn:p"}]}
    overlay = {
        "UserDetailList": [_user("b", "arn:b")],
        "Policies": [{"Arn": "arn:p"}, {"Arn": "arn:q"}],
    }

    once = merge_authorization_details(base, overlay)
    twice = merge_authorization_details(once, overlay)

    assert once == twice


def test_merge_does_not_mutate_inputs():
    base = {"UserDetailList": [_user("a", "arn:a")], "Policies": []}
    overlay = {"UserDetailList": [_user("b", "arn:b")], "Policies": []}

    merge_authorization_details(base, overlay)

    assert len(base["UserDetailList"]) == 1
    assert len(overlay["UserDetailList"]) == 1
