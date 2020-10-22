# CHANGELOG

## Unreleased
* Docker

## 0.2.4 (Unreleased)
* UI
  * Inline Explanation of findings (#115)
  * Vue Router is implemented so you can have routes to reports like http://localhost:8080/#/inline-policies (#116)
  * Better formatting for Privilege Escalation findings (#114)
  * Exclusions config is in its own tab in the UI (#107)

## 0.2.3 (2020-10-12)
* `scan` command now has a `--minimize` option, which you can use to reduce your report size. The example report size was reduced from 3.9MB (ouch!) to 212KB. (Fixes #125)
* UI
  * Credentials Exposure as a new finding (#99)
  * Service Wildcard as a new finding (#82)
* Backend
  * Updated tests to include updated sample data

## 0.2.2 (2020-10-06)
* Excluded actions no longer show up in results (Fixes #106)
* Fixed issue where `*:*` policy would break results due to how the Service Wildcard finding was implemented (Fixes #109)
* Credentials Exposure and Service Wildcard now show up in the data file results
* Exclusions are now applied earlier in the scan
* Backend
  * Vue components are cleaned up - less HTML, more config and JS
  * Unit tests are down from 3.25 minutes to 60 seconds (Fixes #117)

## 0.2.1 (9/25/2020)
* Fixes issue where Inline Policies were showing up as findings even when they were attached to excluded IAM principals. Fixes #104

## 0.2.0 (9/21/2020)
* Major UI uplift: 
  * Added Bar chart of results
  * Upgraded Principals metadata page
  * Standalone page for Inline Policies now
  * Many bug fixes that were present with the previous UI
* Backend
  * Migration to Vue.js
  * Leveraging an updated data JSON file
* `scan-policy-file` command now returns Service Wildcard (#82) and Credentials Exposure (#99). That will not be in the HTML Report for this release though.

## 0.1.8 (2020-08-27)
* UI: The Exclusions configuration was not showing up in the report due to a typo
* Changed `--input` flag to `--input-file` for all commands
* Fixed bug in scan-policy-file command (#79)
* Backend: Improved the JSON output a bit for the new principal policy mapping data file.
* Comment out the principal policy mapping data file for now. Otherwise, if you have a bunch of IAM users, all within different IAM groups, the tool slows down a LOT and you run into loop hell.

## 0.1.7 (2020-08-09)
* UI: Fixed an issue where the Remediation guidance was not showing up in the resulting report. Fixes #70
* Triage Worksheet: Made the values under the Triage worksheet "Type" column more specific - i.e., AWS-Managed Policy, Customer-Managed Policy, Inline Group Policy, Inline User Policy, or Inline Role Policy. Before, it just said "group", "role", "user", or "Policy", which didn't help much.
* Added some backend methods that do not change the functionality. This will help with the eventual UI uplift (and helps with an additional side project)

## 0.1.6 (2020-07-10)
UI:
* Definitions for Risk types are now available via Popovers. Fixes #66
* Renamed "Group", "User", "Role" as "Inline Group Policy", "Inline User Policy", and "Inline Role Policy" respectively. Addresses #63
* Fixes links to the inline policies in case there are duplicate names. Addresses #63
* Moves "Attached to Principal(s)" to the Finding card instead of in the finding details in case there are duplicate policy names. Fixes #63

## 0.1.5 (2020-07-08)
* Made callable via script to partially fix #39
* Move to virtualenv instead of Pipenv

## 0.1.4 (2020-05-26)
* Inline policies are now clearly mapped to their roles.

## 0.1.3 (2020-05-16)
* Excel/CSV export capability
* Table row selection capability

## 0.1.2 (2020-05-14)
Just a few UI fixes:
* Sort columns in Summary table by searching.
* Reasonable size restrictions on "services affected" columns, with Scrollable cells

## 0.1.1 (2020-05-12)
* Bug fix: issue where "Data Exfiltration" count was showing up in the "Resource Exposure" count column in the IAM Principals tab
* Added "Attached to Principals" dropdown card for Customer-Managed and AWS-Managed Policies

## 0.1.0 (2020-05-11)
* Granular exclusions: Fixed issue where exclusions file was including dangling policies in the results (Fixes #33)
* Changed IAM Principals table so that the principals can be sorted according to their risks. This will really help with pentesting

## 0.0.14 (2020-05-07)
* Fix issue where Data Exposure tallies were not showing up in the AWS Managed table correctly.

## 0.0.13 (2020=05-07)
* Windows compatibility fixes

## 0.0.12 (2020-05-07)
* Various UI improvements, like sortable tables. Fixes #22. See https://opensource.salesforce.com/cloudsplaining/ for the latest example.
* Fixes #27 - issue arising from where "expanded_actions" is empty

## 0.0.11 (2020-05-06)
* Fixed an issue arising from policies where "Deny" was used in effect with no resource constraints. Fixes #23.

## 0.0.10 (2020-05-05)
* Removed the recursive credentials method from the `download` command.
* Fixed occasional installation error occurring from outdated Policy Sentry versions.
* Fixed instructions for the `download` command.

## 0.0.9 (2020-05-03)
* HTML report now always shows Trust Policies for Roles, even if they do not allow assumption from a Compute Service. This can help assessors with triaging and pentesters for targeting.

## 0.0.8 (2020-05-03)
* Migrated to GitHub actions with automated Homebrew releases

## 0.0.7 (2020-05-03)
* Added separate tab for IAM Principals
* HTML Report improvements - using tabs now
* Changed the naming of some objects to make the object naming more in line with the AWS IAM API Data Types. https://docs.aws.amazon.com/IAM/latest/APIReference/API_Types.html

## 0.0.6 (2020-05-01)
* Fix `exclude-actions` in the exclusions file - it was not being respected before.
* Add a recursive scanning option.

## 0.0.4 (2020-05-01)
* Provide option to skip opening HTML report (`--skip-open-report`)
* Provide report indicator on whether it is assumable by compute services
* Dropdown menu for report

## 0.0.2 (2020-04-30)
* Quick markdown bug fix

## 0.0.1 (2020-04-30)
* Open sourced!
