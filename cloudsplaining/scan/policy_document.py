from policy_sentry.querying.actions import get_action_data, remove_actions_not_matching_access_level
from cloudsplaining.scan.statement_details import StatementDetails
from cloudsplaining.shared.constants import PRIVILEGE_ESCALATION_METHODS
from cloudsplaining.shared.constants import READ_ONLY_DATA_LEAK_ACTIONS


class PolicyDocument:
    """
    Holds the actual AWS IAM Policy document
    """

    def __init__(self, policy):
        statement_structure = policy.get("Statement", [])
        self.policy = policy
        self.statements = []
        if not isinstance(statement_structure, list):
            statement_structure = [statement_structure]

        for statement in statement_structure:
            self.statements.append(StatementDetails(statement))

    @property
    def json(self):
        """Return the Policy in JSON"""
        return self.policy

    @property
    def all_allowed_actions(self):
        allowed_actions = []
        for statement in self.statements:
            allowed_actions.extend(statement.expanded_actions)
        allowed_actions = list(dict.fromkeys(allowed_actions))
        return allowed_actions

    @property
    def contains_statement_using_not_action(self):
        """If NotAction is used, flag it so the assessor can triage manually"""
        not_action_statements = []
        for statement in self.statements:
            if statement.not_action:
                not_action_statements.append(statement.json)
        return not_action_statements

    @property
    def has_not_resource_with_allow(self):
        """Per the AWS documentation, the NotResource should never be used with the Allow Effect.
        See documentation here. https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_notresource.html#notresource-element-combinations"""
        # If any of these are ever true, "ring the bell"
        not_resource_status = None
        effect_allow_status = None
        result = False
        for statement in self.statements:
            if statement.not_resource:
                not_resource_status = True
            if statement.effect_allow:
                effect_allow_status = True
        # If either of these are ever true. Per AWS docs:
        #   'Be careful using the NotResource element and "Effect": "Allow" in the same statement
        #   or in a different statement within a policy.'
        if not_resource_status and effect_allow_status:
            result = True
        return result

    @property
    def allows_privilege_escalation(self):
        """
        Determines whether or not the policy allows privilege escalation action combinations published by Rhino Security Labs.
        """
        escalations = []
        all_allowed_actions_lowercase = [x.lower() for x in self.all_allowed_actions]
        for key in PRIVILEGE_ESCALATION_METHODS:
            if set(PRIVILEGE_ESCALATION_METHODS[key]).issubset(all_allowed_actions_lowercase):
                escalation = {"type": key, "actions": PRIVILEGE_ESCALATION_METHODS[key]}
                escalations.append(escalation)
        return escalations

    @property
    def permissions_management_without_constraints(self):
        result = []
        for statement in self.statements:
            if statement.permissions_management_actions_without_constraints:
                result.extend(statement.permissions_management_actions_without_constraints)
        return result

    @property
    def write_actions_without_constraints(self):
        result = []
        for statement in self.statements:
            if statement.write_actions_without_constraints:
                result.extend(statement.write_actions_without_constraints)
        return result

    @property
    def tagging_actions_without_constraints(self):
        result = []
        for statement in self.statements:
            if statement.tagging_actions_without_constraints:
                result.extend(statement.write_actions_without_constraints)
        return result

    def allows_specific_actions_without_constraints(self, specific_actions):
        allowed = []
        if not isinstance(specific_actions, list):
            raise Exception("Please supply a list of actions.")

        # Doing this nested for loop so we can get results that use the official CamelCase actions, and
        # the results don't fail if given lowercase input.
        # this is less efficient but more accurate and the results are pretty :)
        for specific_action in specific_actions:
            for allowed_action in self.all_allowed_actions:
                if specific_action.lower() == allowed_action.lower():
                    allowed.append(allowed_action)
        return allowed

    @property
    def allows_data_leak_actions(self):
        return self.allows_specific_actions_without_constraints(READ_ONLY_DATA_LEAK_ACTIONS)
