# open-cloudsplaining-jira-ticket

1. Create an API Token for JIRA Cloud: https://confluence.atlassian.com/cloud/api-tokens-938839638.html
2. Generate your Cloudsplaining report
3. Install stuff for this script

```bash
pip3 install jira
pip3 install click
```

4. Open your JIRA issue.

```bash
python open_jira_ticket.py \
    --project PROJ \
    --auth-file authz.json \
    --report-file report.html \
    --triage-file triage.csv \
    --data-file data.json \
    --server http://myserver.atlassian.net
```

