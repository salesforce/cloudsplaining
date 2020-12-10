# Release Drafter

1. Every time a PR is merged, the draft release note is updated 
   to add a entry for this change
2. We have a github release-drafter action which automatically 
   does this after a PR is merged.
3. It also increments the release version if this is the first PR for a new release. 
   Note: This will only update the draft release note. We still have to bump 
   the version as per [versioning document](https://github.com/salesforce/cloudsplaining/blob/master/docs/contributing/versioning.md)
4. When we are ready to publish the release, we use the drafted 
   release note to do so.
5. Release drafter categorizes the changes in the release into `Features`, `BugFixes`, `Maintenance`, 
   `Documentation` categories as per the labels added to the PR


Adding labels to the PR:

- Contributors can add appropriate label 
  to the PR (`feature`, `bugfix`, `documentation`, `maintenance` etc.)
- If PR contributor does not have the permission, 
  Maintainers should add the label.
