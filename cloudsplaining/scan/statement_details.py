import logging
from cloudsplaining.shared.utils import remove_read_level_actions, remove_wildcard_only_actions
from policy_sentry.analysis.analyze import determine_actions_to_expand
from policy_sentry.querying.actions import remove_actions_not_matching_access_level, get_actions_matching_arn
from policy_sentry.util.arns import get_service_from_arn, does_arn_match
from policy_sentry.querying.arns import get_raw_arns_for_service, get_matching_raw_arn
from policy_sentry.querying.all import get_all_actions
logger = logging.getLogger(__name__)

all_actions = get_all_actions()


class StatementDetails:
    """
    Analyzes individual statements within a policy
    """

    def __init__(self, statement):
        self.json = statement
        self.statement = statement
        self.actions = self._actions()
        self.resources = self._resources()
        self.not_action = self._not_action()
        self.not_resource = self._not_resource()
        self.effect = statement["Effect"]

    def _actions(self):
        """Holds the actions in a statement"""
        actions = self.statement.get("Action")
        if not actions:
            return []
        if not isinstance(actions, list):
            actions = [actions]
        return actions

    def _resources(self):
        """Holds the resource ARNs in a statement"""
        resources = self.statement.get("Resource")
        if not resources:
            return []
        # If it's a string, turn it into a list
        if not isinstance(resources, list):
            resources = [resources]
        return resources

    def _not_action(self):
        """Holds the NotAction details.
        We won't do anything with it - but we will flag it as something for the assessor to triage."""
        not_action = self.statement.get("NotAction")
        if not not_action:
            return []
        if not isinstance(not_action, list):
            not_action = [not_action]
        return not_action

    def _not_resource(self):
        """Holds the NotResource details.
        We won't do anything with it - but we will flag it as something for the assessor to triage."""
        not_resource = self.statement.get("NotResource")
        if not not_resource:
            return []
        if not isinstance(not_resource, list):
            not_resource = [not_resource]
        return not_resource

    @property
    def not_action_effective_actions(self):
        """If NotAction is used, calculate the allowed actions - i.e., what it would be """
        # def determine_scope(arn):
        services_in_scope = []
        effective_actions = []
        if not self.not_action:
            return False
        not_actions_expanded = determine_actions_to_expand(self.not_action)
        not_actions_expanded_lowercase = [x.lower() for x in not_actions_expanded]

        # Effect: Allow && Resource != "*"
        if self.has_resource_constraints and self.effect_allow:
            opposite_actions = []
            for arn in self.resources:
                actions_specific_to_arn = get_actions_matching_arn(arn)
                if actions_specific_to_arn:
                    opposite_actions.extend(get_actions_matching_arn(arn))

            for opposite_action in opposite_actions:
                # If it's in NotActions, then it is not an action we want
                if opposite_action.lower() in not_actions_expanded_lowercase:
                    pass
                # Otherwise add it
                else:
                    effective_actions.append(opposite_action)
            effective_actions.sort()
            return effective_actions
        # Effect: Allow && Resource == "*"
        elif not self.has_resource_constraints and self.effect_allow:
            logger.warning("\tThe policy with Effect Allow uses NotAction without any resource constraints: %s" % self.statement)

            # Then we calculate the reverse using all_actions
            for action in all_actions:
                # If it's in NotActions, then it is not an action we want
                if action.lower() in not_actions_expanded_lowercase:
                    pass
                    # Otherwise add it
                else:
                    effective_actions.append(action)
            effective_actions.sort()
            return effective_actions
        elif self.has_resource_constraints and self.effect_deny:
            logger.critical("Haven't decided if we support Effect Deny here?")
        elif not self.has_resource_constraints and self.effect_deny:
            logger.critical("Haven't decided if we support Effect Deny here?")

    @property
    def has_not_resource_with_allow(self):
        """Per the AWS documentation, the NotResource should never be used with the Allow Effect.
        See documentation here. https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_notresource.html#notresource-element-combinations"""
        result = False
        if self.not_resource:
            if self.effect_allow:
                result = True
        return result

    @property
    def expanded_actions(self):
        if self.actions:
            expanded = determine_actions_to_expand(self.actions)
            expanded.sort()
            return expanded
        elif self.not_action:
            return self.not_action_effective_actions

    @property
    def effect_deny(self):
        if self.effect == "Deny":
            return True
        else:
            return False

    @property
    def effect_allow(self):
        if self.effect == "Allow":
            return True
        else:
            return False

    @property
    def services_in_use(self):
        service_prefixes = []
        for action in self.expanded_actions:
            service, action_name = action.split(":")
            if service not in service_prefixes:
                service_prefixes.append(service)
        service_prefixes.sort()
        return service_prefixes

    @property
    def has_resource_constraints(self):
        answer = True
        if len(self.resources) == 0:
            # This is probably a NotResources situation which we do not support.
            pass
        if len(self.resources) == 1:
            if self.resources[0] == "*":
                answer = False
        elif len(self.resources) > 1:
            # It's possible that someone writes a bad policy that includes both a resource ARN as well as a wildcard.
            for resource in self.resources:
                if resource == "*":
                    answer = False
        return answer

    @property
    def permissions_management_actions_without_constraints(self):
        result = []
        if not self.has_resource_constraints:
            result = remove_actions_not_matching_access_level(self.expanded_actions, "Permissions management")
        return result

    @property
    def write_actions_without_constraints(self):
        result = []
        if not self.has_resource_constraints:
            result = remove_actions_not_matching_access_level(self.expanded_actions, "Write")
        return result

    @property
    def tagging_actions_without_constraints(self):
        result = []
        if not self.has_resource_constraints:
            result = remove_actions_not_matching_access_level(self.expanded_actions, "Tagging")
        return result

    @property
    def missing_resource_constraints(self):
        actions_missing_resource_constraints = []
        if len(self.resources) == 1:
            if self.resources[0] == "*":
                actions_missing_resource_constraints = remove_wildcard_only_actions(self.expanded_actions)
        return actions_missing_resource_constraints

    def missing_resource_constraints_for_modify_actions(self, always_look_for_actions=None):
        if always_look_for_actions is None:
            always_look_for_actions = []
        actions_missing_resource_constraints = self.missing_resource_constraints

        always_actions_found = []
        for action in actions_missing_resource_constraints:
            if action.lower() in [x.lower() for x in always_look_for_actions]:
                always_actions_found.append(action)
        modify_actions_missing_constraints = remove_read_level_actions(actions_missing_resource_constraints)
        modify_actions_missing_constraints = modify_actions_missing_constraints + always_actions_found
        return modify_actions_missing_constraints
