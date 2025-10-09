### How do I fix the problem?

We suggest two options for remediating each finding: 

1. Leveraging Policy Sentry, courtesy of Kinnaird McQuade, which generates policies with resource ARN constraints at user-specified access levels automagically. 
2. Manually rewriting the policies

#### Leveraging Policy Sentry

For guidance on how to use Policy Sentry, please see the documentation here. This is highly suggested - within 10 minutes of learning the tool, creating a secure IAM policy becomes a matter of:

* Generating the YAML template
  * `policy_sentry create-template --output-file crud.yml --template-type crud`
* Literally copying/pasting resource ARNs into the template
* Running the write-policy command:
  * `policy_sentry write-policy --input-file crud.yml`

  
####  Manually rewriting the IAM Policies

For guidance on how to write secure IAM Policies by hand, see the tutorial here. Just be aware - you'll spend a lot of time looking at the AWS Documentation on IAM Actions, Resources, and Condition Keys, which can become quite tedious and time-consuming.

### Validating Results?

1. Use the Parliament web app to validate your policies: https://parliament.summitroute.com/
2. Use the Cloudsplaining `scan-policy-file` command to validate your policies: https://cloudsplaining.readthedocs.io/en/latest/user-guide/scan-policy-file/
