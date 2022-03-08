import pprint

import invoke
import requests

import clickup

webhook = {
    "endpoint": "https://clickup-task-aggregator.herokuapp.com/handle-task-status-update",
    "events": [
        "taskStatusUpdated",
        "keyResultDeleted",
    ],  # ClickUp's API doesn't accept just one (bug)
    "status": "active",
}


@invoke.task
def install_webhook(ctx, team_id):
    response = requests.post(
        f"https://api.clickup.com/api/v2/team/{team_id}/webhook",
        headers={"Authorization": clickup.config["api_token"]},
        data=webhook,
    )
    pprint.pprint(response.json() if response.ok else (response.status_code, response.content))


@invoke.task
def modify_webhook(ctx, webhook_id):
    response = requests.put(
        f"https://api.clickup.com/api/v2/webhook/{webhook_id}",
        headers={"Authorization": clickup.config["api_token"]},
        data=webhook,
    )
    pprint.pprint(response.json() if response.ok else (response.status_code, response.content))


@invoke.task
def query_webhooks(ctx, team_id):
    response = requests.get(
        f"https://api.clickup.com/api/v2/team/{team_id}/webhook",
        headers={"Authorization": clickup.config["api_token"]},
    )
    pprint.pprint(response.json() if response.ok else (response.status_code, response.content))
