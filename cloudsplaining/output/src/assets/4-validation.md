##### Validating remediated policies

After you've rewritten your IAM policy, we suggest two options for validating that it will pass Cloudsplaining and alleviate any remaining concerns:

* Run Cloudsplaining's `scan-policy-file` command, which scans a single JSON policy file instead of the entire AWS Account's Authorization details.
* Leveraging [Parliament by Duo-Labs](https://github.com/duo-labs/parliament/"), courtesy of [Scott Piper](https://twitter.com/0xdabbad00)


##### Using Cloudsplaining to Validate your Remediated Policies

You can validate that your remediated policy passes Cloudsplaining by running the following command:

```cloudsplaining scan-policy-file --input-file policy.json --exclusions-file exclusions.yml```

When there are no more results, it passes!


##### Using Parliament to Lint your Policies

parliament is an AWS IAM linting library. It reviews policies looking for problems such as:

* malformed JSON
* missing required elements
* incorrect service prefix and action names
* incorrect resources or conditions for the actions provided
* type mismatches
* bad policy patterns

This library duplicates (and adds to!) much of the functionality in the web console page when reviewing IAM policies in the browser.

You can use Parliament to scan your IAM policy by visiting the Web Page! [https://parliament.summitroute.com/](https://parliament.summitroute.com/)