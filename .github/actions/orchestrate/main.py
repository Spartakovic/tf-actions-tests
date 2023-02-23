#!/usr/bin/env python

import os
import sys
import json
from github import Github

path = sys.argv[0]

event = json.loads(os.getenv("GITHUB_EVENT"))
github_token = os.getenv("GITHUB_TOKEN")
github_repo = os.getenv("GITHUB_REPOSITORY")

github = Github(login_or_token=github_token)
all_open_prs = github.get_repo(github_repo).get_pulls(state='open')
oldest_open_pr = all_open_prs.reversed[0]

latest_closed_pr = github.get_repo(github_repo).get_pulls(state='closed', sort='updated').reversed[0]

if event['name'] == 'pull_request':
    if event['action'] in ['opened', 'reopened', 'synchronize']:
        if not all_open_prs:
            print("No open PRs found. Running terraform plan")
        else:
            print("There are currently open PRs. Skipping terraform plan")
    if event['action'] in ['closed']:
        if latest_closed_pr.number == event['number']:
            github.get_repo(github_repo).get_workflow("orchestration.yml").create_dispatch(oldest_open_pr.ref, {"command_type": "plan"})
elif event['name'] == 'push':
    if oldest_open_pr.head.ref == event['ref']:
        print("This is the oldest open PR. Running terraform plan")
    else:
        print("This is not the oldest open PR. Skipping terraform plan")
elif event['name'] == 'workflow_dispatch':
    if event['inputs']['command_type'] == 'plan':
        print("Running terraform plan")
    elif event['inputs']['command_type'] == 'apply':
        print("Running terraform apply")
