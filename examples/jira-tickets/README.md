# open-cloudsplaining-jira-ticket

1. Create an API Token for JIRA Cloud: https://confluence.atlassian.com/cloud/api-tokens-938839638.html
2. Generate your Cloudsplaining report
3. Install stuff for this script (`pip3 install -r requirements.txt`)
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

