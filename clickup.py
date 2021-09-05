#!/usr/bin/env python3
import datetime
import json
import os
import sys

import requests
import termplot

with open(os.path.expanduser("~/.config/gnome-clickup-dash/clickup.config.json")) as f:
    config = json.load(f)


def fetch():
    due_tasks = []
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

    now = datetime.datetime.utcnow()
    completed_tasks = requests.get(
        "https://clickup-task-aggregator.herokuapp.com/get-completed",
        headers={"Authorization": config["task_aggregator_api_token"]},
        params={"start": (now - datetime.timedelta(weeks=1)).isoformat(), "end": now.isoformat()}
    ).json()
    print(completed_tasks)

    completed = len(completed_tasks)
    due = len(due_tasks)
    emoji = "sunglasses" if completed >= config["task_goal"] else "runner"
    print(f"{completed} / {config['task_goal']}, <span color='lightblue'>due: {due}</span> :{emoji}: | iconName=object-select-symbolic")
    print("---")
    termplot.plot([0, 1, 2, 3], plot_height=3)
    if due > 0:
        for task in due_tasks:
            print(f"{task['name'][:30]} | iconName=mail-forward-symbolic href={task['url']}")
    # if completed > 0:
    #     for task in completed_tasks:
    #         print(f"{task['name'][:30]} | iconName=object-select-symbolic href={task['url']}")


if __name__ == '__main__':
    try:
        fetch()
    except ConnectionError:
        print("No Network")

    print("---")
    print("Open Clickup | href=https://app.clickup.com/")
    print(f"Refresh (last: {datetime.datetime.now():%H:%M}) | refresh=true")
