#!/usr/bin/env python3
import datetime
import json
import logging
import os
import pathlib
import sys
import tempfile

import caldav
import pytz
import requests

from . import models

tmp = pathlib.Path(tempfile.gettempdir())
logging.basicConfig(filename=tmp / "gnome-clickup-dash.log", level=logging.DEBUG)
logging.info("Starting")
OFFSET_INTO_NEW_DAY = datetime.timedelta(hours=4, minutes=30)
DAYS_BACK = 10
with open(os.path.expanduser("~/.config/gnome-clickup-dash/clickup.config.json")) as f:
    config = json.load(f)


def points_to_string(points: float):
    return str(int(points) if int(points) == points else points)


def fetch():
    due_tasks = []
    for workspace in config["workspaces"]:
        response = requests.get(
            f"https://api.clickup.com/api/v2/view/{workspace['still_due_view_id']}/task",
            headers={"Authorization": config["api_token"]},
            data={"page": 0},
        )
        if response.ok:
            due_tasks.extend(response.json()["tasks"])
        else:
            logging.error(f"Invalid response received {response.status_code}")
            sys.exit(1)

    start_day = datetime.date.today() - datetime.timedelta(days=DAYS_BACK)
    start_day_time = datetime.datetime.combine(start_day, datetime.datetime.min.time()).astimezone()  # local 00:00
    response = requests.get(
        "https://clickup-task-aggregator.herokuapp.com/get-completed",
        headers={"Authorization": config["task_aggregator_api_token"]},
        params={
            "start": (start_day_time + OFFSET_INTO_NEW_DAY).isoformat(),
            "end": datetime.datetime.utcnow().isoformat(),
        },
    )
    # print("... aggregated tasks", file=sys.stderr)
    if not response.ok:
        logging.error(f"Invalid response received {response.status_code}")
        sys.exit(1)
    completed_tasks = response.json()

    per_day = [0.0] * (DAYS_BACK + 1)
    tasks_of_day = [[] for _ in range(DAYS_BACK + 1)]
    for task in map(models.CompletedTaskLog.parse_obj, completed_tasks):
        delta = (task.timestamp.astimezone(pytz.utc) - OFFSET_INTO_NEW_DAY) - start_day_time
        per_day[delta.days] += task.points
        tasks_of_day[delta.days].append(task)
    return due_tasks, per_day, tasks_of_day


def construct_menu():
    due_tasks, per_day, tasks_of_day = fetch()
    points_today = per_day[-1]
    due = len(due_tasks)
    emoji = "sunglasses" if points_today >= config["task_goal"] else "runner"

    clearfix = "<span color='blue'> </span>"
    green = "color='green'"
    print(
        f"{clearfix}<span {green if points_today >= config['task_goal'] else ''}>"
        f"{points_to_string(points_today)} / {config['task_goal']}</span>, "
        f"<span color='orange'>due: {due}</span> :{emoji}: | iconName=object-select-symbolic"
    )
    print("---")

    title = " ".join(
        map(
            lambda x: f"<span color='{'green' if x >= config['task_goal'] else 'orange'}'>{points_to_string(x)}</span>",
            per_day,
        )
    )
    print(f"{clearfix}<tt><b>{title}</b></tt>")
    if due > 0:
        print("---")
        for task in due_tasks[:6]:
            print(f"{task['name'][:30]} | iconName=media-playback-start-symbolic")
            print(f"--Open task on ClickUp | href={task['url']} iconName=applications-other-symbolic")
            print(
                "--Complete this task | iconName=object-select-symbolic bash"
                f"='/home/peter/bin/clickup close-task {task['id']}'"
            )
        if due > 6:
            print(f"... and {due - 6} more")
    if points_today > 0:
        print("---")
        for task in tasks_of_day[-1]:
            print(
                f"{task.task_name[:30]} [{task.points}p] | iconName=object-select-symbolic "
                "href=https://app.clickup.com/t/{task.task_id}"
            )


def main():
    try:
        construct_menu()
    except ConnectionError:
        print("No Network")
        logging.exception("Connection Error")

    logging.info("Finished")
    print("---")
    print("Open Clickup | href=https://app.clickup.com/")
    print(f"Refresh (last: {datetime.datetime.now():%H:%M}) | refresh=true")


cli = caldav.DAVClient("https://waldcloud.hopto.org:2023/dav/peter/calendars/", username="leser", password="p1140")
principal = cli.principal()
# principal.calendar_home_set


def get_list_tasks(list_id):
    page = 0
    response = requests.get(
        f"https://api.clickup.com/api/v2/list/{list_id}/task",
        headers={"Authorization": config["api_token"]},
        data={"page": page},
    ).json()
    return response["tasks"]


def export_list_to_caldav(list_id, name):
    calendar = principal.calendar_home_set.make_calendar(name)
    for task in get_list_tasks(list_id):
        kwargs = {}
        if task["due_date"]:
            kwargs["due"] = datetime.datetime.fromtimestamp(int(task["due_date"]) / 1000).date()
        response = calendar.add_todo(summary=task["name"], **kwargs)
        print(f"Created {task['name']} due on {kwargs.get('due')}")


def export_all(space_id=10931387):
    for list in requests.get(
        f"https://api.clickup.com/api/v2/space/{space_id}/list",
        headers={"Authorization": config["api_token"]},
    ).json()["lists"]:
        print(list["id"], list["name"])
        export_list_to_caldav(list["id"], list["name"])

    for folder in requests.get(
        f"https://api.clickup.com/api/v2/space/{space_id}/folder",
        headers={"Authorization": config["api_token"]},
    ).json()["folders"]:
        print(folder["name"])
        for list in requests.get(
            f"https://api.clickup.com/api/v2/folder/{folder['id']}/list",
            headers={"Authorization": config["api_token"]},
        ).json()["lists"]:
            print(list["id"], folder["name"] + "." + list["name"])
            export_list_to_caldav(list["id"], folder["name"] + "." + list["name"])


if __name__ == "__main__":
    main()
