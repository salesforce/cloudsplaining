<div id="validation-guidance-description"> <h5>Validating remediated policies</h5></div>

After you've rewritten your IAM policy, we suggest two options for validating that it will pass Cloudsplaining and alleviate any remaining concerns:

<div id="validation-guidance-pt1-bullet-points">
<ul>
  <li>Run Cloudsplaining's <code>scan-policy-file</code> command, which scans a single JSON policy file instead of the entire AWS Account's Authorization details. </li>
  <li>Leveraging <a href="https://github.com/duo-labs/parliament/">Parliament by Duo-Labs</a>, courtesy of <a href="https://twitter.com/0xdabbad00">Scott Piper</a>)</li>
</ul>
</div>

<div id="validation-using-cloudsplaining"> <h6>Using Cloudsplaining to Validate your Remediated Policies</h6></div>

You can validate that your remediated policy passes Cloudsplaining by running the following command:

```cloudsplaining scan-policy-file --file policy.json --exclusions-file exclusions.yml```

When there are no more results, it passes!

<div id="validation-using-parliament"> <h6>Using Parliament to Lint your Policies</h6></div>

parliament is an AWS IAM linting library. It reviews policies looking for problems such as:

<div id="validation-guidance-pt2-bullet-points">
<ul>
  <li>malformed JSON </li>
  <li>missing required elements</li>
  <li>incorrect service prefix and action names</li>
  <li>incorrect resources or conditions for the actions provided</li>
  <li>type mismatches</li>
  <li>bad policy patterns</li>
</ul>
</div>

This library duplicates (and adds to!) much of the functionality in the web console page when reviewing IAM policies in the browser.

You can use Parliament to scan your IAM policy with the following command:

```parliament --file policy.json```
