# Clickup Dashboard Extension
... for the Gnome Task Bar, using Argos - a BitBar-like customization tool for Gnome Extensions!

Install Argos ![here](https://extensions.gnome.org/extension/1176/argos/).

This little project shows a summary of ClickUp workspaces' progress for a user.
To configure it, please create `~/.config/gnome-clickup-dash/clickup.config.json` and fill it with the following content:

```json
{
  "api_token": "pk_*_*",
  "workspaces": [
    {
      "nickname": "Workspace 1",
      "id": "123456",
      "completed_view_id": "asdfg-36",
      "still_due_view_id": "asdfg-43"
    },
    {
      "nickname": "Workspace 2",
      "id": "7891011",
      "completed_view_id": "asdfg-218",
      "still_due_view_id": "asdfg-225"
    }
  ],
  "task_goal": 3
}
```
You can obtain the API token in your personal account settings ("-> Apps").

For each workspace, define a completed_view, which essentially filters for all the tasks you've done, say, today.
Similarly, introduce a still_due_view, that filters for all the tasks that are scheduled to today (or similar).

Define a personal `task_goal` for you to complete every day (or whatever time period you're using).

Have fun!
