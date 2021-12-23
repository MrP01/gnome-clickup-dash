#!/usr/bin/env python3
import datetime
import json
import os
import sys

import pytz
import requests

import models

with open(os.path.expanduser("~/.config/gnome-clickup-dash/clickup.config.json")) as f:
    config = json.load(f)

OFFSET_INTO_NEW_DAY = datetime.timedelta(hours=4, minutes=30)
DAYS_BACK = 10


def points_to_string(points: float):
    return str(int(points) if int(points) == points else points)


def fetch():
    due_tasks = []
    for workspace in config["workspaces"]:
        response = requests.get(
            f"https://api.clickup.com/api/v2/view/{workspace['still_due_view_id']}/task",
            headers={"Authorization": config["api_token"]}, data={"page": 0}
        )
        print(".. Workspace requested", file=sys.stderr)
        if response.ok:
            due_tasks.extend(response.json()["tasks"])
        else:
            print("ClickUp error")
            sys.exit(1)

    start_day = datetime.date.today() - datetime.timedelta(days=DAYS_BACK)
    start_day_time = datetime.datetime.combine(start_day, datetime.datetime.min.time()).astimezone()  # local 00:00
    response = requests.get(
        "https://clickup-task-aggregator.herokuapp.com/get-completed",
        headers={"Authorization": config["task_aggregator_api_token"]},
        params={"start": (start_day_time + OFFSET_INTO_NEW_DAY).isoformat(), "end": datetime.datetime.utcnow().isoformat()}
    )
    print(".. aggregated tasks", file=sys.stderr)
    assert response.ok
    completed_tasks = response.json()

    per_day = [0] * (DAYS_BACK + 1)
    tasks_of_day = [list() for _ in range(DAYS_BACK + 1)]
    for task in map(models.CompletedTaskLog.parse_obj, completed_tasks):
        delta = (task.timestamp.astimezone(pytz.utc) - OFFSET_INTO_NEW_DAY) - start_day_time
        per_day[delta.days] += task.points
        tasks_of_day[delta.days].append(task)

    points_today = per_day[-1]
    due = len(due_tasks)
    emoji = "sunglasses" if points_today >= config["task_goal"] else "runner"

    clearfix = "<span color='blue'> </span>"
    green = "color='green'"
    print(f"{clearfix}<span {green if points_today >= config['task_goal'] else ''}>{points_to_string(points_today)} / {config['task_goal']}</span>, "
          f"<span color='orange'>due: {due}</span> :{emoji}: | iconName=object-select-symbolic")
    print("---")
    print(f"{clearfix}<tt><b>" + " ".join(map(
        lambda x: f"<span color='{'green' if x >= config['task_goal'] else 'orange'}'>{points_to_string(x)}</span>",
        per_day
    )) + "</b></tt>")
    if due > 0:
        print("---")
        for task in due_tasks[:6]:
            print(f"{task['name'][:30]} | iconName=mail-forward-symbolic href={task['url']}")
        if due > 6:
            print(f"... and {due - 6} more")
    if points_today > 0:
        print("---")
        for task in tasks_of_day[-1]:
            print(f"{task.task_name[:30]} [{task.points}p] | iconName=object-select-symbolic href=https://app.clickup.com/t/{task.task_id}")


if __name__ == '__main__':
    try:
        fetch()
    except ConnectionError:
        print("No Network")

    print("---")
    print("Open Clickup | href=https://app.clickup.com/")
    print(f"Refresh (last: {datetime.datetime.now():%H:%M}) | refresh=true")
