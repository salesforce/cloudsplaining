from cloudsplaining.scan.resource_policy_document import ResourcePolicyDocument


def test_resource_policy_document():
    # given
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Principal": {"AWS": "*"},
                "Effect": "Allow",
                "Action": [
                    "SNS:Subscribe",
                    "SNS:Publish",
                ],
                "Resource": "*",
            }
        ],
    }

    # when
    policy_doc = ResourcePolicyDocument(policy=policy)

    # then
    assert policy_doc.internet_accessible_actions == ["SNS:Subscribe", "SNS:Publish"]


def test_resource_policy_document_restricted_by_arn():
    # given
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Principal": {"AWS": "*"},
                "Effect": "Allow",
                "Action": [
                    "SNS:Subscribe",
                    "SNS:Publish",
                ],
                "Resource": "*",
                "Condition": {
                    "ForAnyValue:ARNEquals": {
                        "AWS:SourceArn": [
                            "arn:aws:iam::012345678910:role/SomeTestRoleForTesting",
                            "arn:aws:iam::012345678910:role/OtherRole",
                        ]
                    },
                },
            }
        ],
    }

    # when
    policy_doc = ResourcePolicyDocument(policy=policy)

    # then
    assert policy_doc.internet_accessible_actions == []


def test_resource_policy_document_restricted_by_cidr():
    # given
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Principal": {"AWS": "*"},
                "Effect": "Allow",
                "Action": [
                    "SNS:Subscribe",
                    "SNS:Publish",
                ],
                "Resource": "*",
                "Condition": {
                    "IpAddress": {
                        "AWS:SourceIP": [
                            "10.0.0.0/16",
                        ]
                    }
                },
            }
        ],
    }

    # when
    policy_doc = ResourcePolicyDocument(policy=policy)

    # then
    assert policy_doc.internet_accessible_actions == []


def test_resource_policy_document_restricted_by_org_id():
    # given
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Principal": {"AWS": "*"},
                "Effect": "Allow",
                "Action": [
                    "SNS:Subscribe",
                    "SNS:Publish",
                ],
                "Resource": "*",
                "Condition": {
                    "StringEquals": {
                        "AWS:PrincipalOrgID": "o-xxxxxxxxxx",
                    }
                },
            }
        ],
    }

    # when
    policy_doc = ResourcePolicyDocument(policy=policy)

    # then
    assert policy_doc.internet_accessible_actions == []


def test_resource_policy_document_restricted_by_user_id():
    # given
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Principal": {"AWS": "*"},
                "Effect": "Allow",
                "Action": [
                    "SNS:Subscribe",
                    "SNS:Publish",
                ],
                "Resource": "*",
                "Condition": {
                    "StringLike": {
                        "AWS:userid": "AROAI1111111111111111:*",
                    }
                },
            }
        ],
    }

    # when
    policy_doc = ResourcePolicyDocument(policy=policy)

    # then
    assert policy_doc.internet_accessible_actions == []
