#!/usr/bin/env python

import os
import sys
import json
from github import Github

path = sys.argv[0]

event = json.loads(os.getenv("GITHUB_EVENT"))
event_name = os.getenv("GITHUB_EVENT_NAME")
github_token = os.getenv("GITHUB_TOKEN")
github_repo = os.getenv("GITHUB_REPOSITORY")

github = Github(login_or_token=github_token)
all_open_prs = github.get_repo(github_repo).get_pulls(state='open', direction='asc')
oldest_open_pr = all_open_prs[0] if all_open_prs.totalCount > 0 else None

all_closed_prs = github.get_repo(github_repo).get_pulls(state='closed', sort='updated', direction='desc')
latest_closed_pr = all_closed_prs[0] if all_closed_prs.totalCount > 0 else None

if event_name == 'pull_request':
    if event['action'] in ['opened', 'reopened', 'synchronize']:
        if not all_open_prs:
            print("No open PRs found. Running terraform plan")
        else:
            print("There are currently open PRs. Skipping terraform plan")
    if event['action'] in ['closed']:
        if latest_closed_pr.number == event['number']:
            github.get_repo(github_repo).get_workflow("orchestration.yml").create_dispatch(oldest_open_pr.ref, {"command_type": "plan"})
elif event_name == 'push':
    if not oldest_open_pr:
        print("No pr's open. Running terraform plan")
    elif oldest_open_pr.head.ref == event['ref']:
        print("This is the oldest open PR. Running terraform plan")
    else:
        print("This is not the oldest open PR. Skipping terraform plan")
elif event_name == 'workflow_dispatch':
    if event['inputs']['command_type'] == 'plan':
        print("Running terraform plan")
    elif event['inputs']['command_type'] == 'apply':
        print("Running terraform apply")
