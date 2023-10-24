# notion-pipedream-todolistBot
A python bot that creates a todo item for all active members in a notion team's todolist.

Using pipedream's "New Page in Database" Trigger.

If you dont need the filtering, simply change the `pages = get_pages_with_filter(MEMBERS_DATABASE, active_filter)` call to use `get_pages()`

You need to set the following
```
NOTION_TOKEN = ""
TODOS_DATABASE = ""
MEMBERS_DATABASE = ""
```
