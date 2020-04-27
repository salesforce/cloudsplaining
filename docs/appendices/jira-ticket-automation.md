# Jira Ticket Automation

You can leverage the Python script `open_jira_ticket.py` as an example of how to open up JIRA tickets automatically with a Cloudsplaining report description and attachments. This can speed up your assessment process.

See the script here: https://github.com/salesforce/cloudsplaining/tree/master/examples/jira-tickets.

### Steps
1. Create an API Token for JIRA Cloud: https://confluence.atlassian.com/cloud/api-tokens-938839638.html
2. Generate your Cloudsplaining report
3. Install the dependencies for this script (`pip3 install -r requirements.txt`)
3. Open your JIRA issue.

```bash
python open_jira_ticket.py \
    --project PROJ \
    --auth-file authz.json \
    --report-file report.html \
    --triage-file triage.csv \
    --data-file data.json \
    --server http://myserver.atlassian.net
```


