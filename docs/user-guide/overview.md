# Overview

TODO: Insert diagram of process.

* Download authorization details
* Create custom Exclusions file
* Run report

* Find false positives
* Update exclusions file
* Run report again

## Commands

* Download the Account Authorization details JSON file
    - `cloudsplaining download --profile default --output default-account-details.json`
* Generate your custom exclusions file
    - `cloudsplaining create-exclusions-file --output-file exclusions.yml`
* Scan the Account Authorization details
    - `cloudsplaining scan --file default-account-details.json --exclusions-file exclusions.yml`
    - This generates three files: (1) The single-file HTML report, (2) The triage CSV worksheet, and (3) The raw JSON data file
