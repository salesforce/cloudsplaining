# CHANGELOG

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
