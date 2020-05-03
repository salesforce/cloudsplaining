# CHANGELOG

## 0.0.7 (Unreleased)
* Changed the `Principal` object to `PrincipalDetail` object to make the object naming more in line with the AWS IAM API Data Types. https://docs.aws.amazon.com/IAM/latest/APIReference/API_Types.html
* Added logic for mapping Principals vs Policies
* Going to add the above mapping + relation to findings to the HTML Report

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
