#!/usr/bin/env python3
import requests
import datetime
import json
import os
import sys

with open(os.path.expanduser("~/.config/gnome-clickup-dash/clickup.config.json")) as f:
    config = json.load(f)


def fetch():
    due_tasks = []
    completed_tasks = []
    for workspace in config["workspaces"]:
        response = requests.get(
            f"https://api.clickup.com/api/v2/view/{workspace['still_due_view_id']}/task",
            headers={"Authorization": config["api_token"]}, data={"page": 0}
        )
        if response.ok:
            due_tasks.extend(response.json()["tasks"])
        else:
            print("ClickUp error")
            sys.exit(1)
        response = requests.get(
            f"https://api.clickup.com/api/v2/view/{workspace['completed_view_id']}/task",
            headers={"Authorization": config["api_token"]}, data={"page": 0}
        )
        if response.ok:
            completed_tasks.extend(response.json()["tasks"])
        else:
            print("ClickUp error")
            sys.exit(1)

    completed = len(completed_tasks)
    due = len(due_tasks)
    emoji = "sunglasses" if completed >= config["task_goal"] else "runner"
    print(f"{completed} / {config['task_goal']}, due: {due} :{emoji}: | iconName=object-select-symbolic")
    if due > 0:
        print("---")
        for task in due_tasks:
            print(f"{task['name'][:30]} | iconName=mail-forward-symbolic href={task['url']}")
    if completed > 0:
        print("---")
        for task in completed_tasks:
            print(f"{task['name'][:30]} | iconName=object-select-symbolic href={task['url']}")


try:
    fetch()
except ConnectionError:
    print("No Network")

print("---")
print("Open Clickup | href=https://app.clickup.com/")
print(f"Refresh (last: {datetime.datetime.now():%H:%M}) | refresh=true")
