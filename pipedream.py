import threading
import requests
NOTION_TOKEN = ""
TODOS_DATABASE = ""
MEMBERS_DATABASE = ""

from pipedream.script_helpers import (steps, export)

#TODO_MESSAGE = "TEST MESSAGE SIMPLE"
TODO_MESSAGE = steps["trigger"]["event"]["properties"]['Name']['title'][0]['plain_text']


headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}


def create_page(data: dict, databaseID: str):
    #print(f"Creating page {data.get('Name').get('title')[0].get('text').get('content')} for {data.get('PERSON').get('relation')[0].get('id')}")
    create_url = "https://api.notion.com/v1/pages"

    payload = {"parent": {"type": "database_id",
                          "database_id": databaseID}, "properties": data}

    response = requests.post(create_url, headers=headers, json=payload)
    # print(res.status_code)
    return response


def get_pages(databaseID: str, num_pages=None):
    """
    If num_pages is None, get all pages, otherwise just the defined number.
    """
    url = f"https://api.notion.com/v1/databases/{databaseID}/query"

    get_all = num_pages is None
    page_size = 100 if get_all else num_pages

    payload = {"page_size": page_size}
    response = requests.post(url, json=payload, headers=headers)

    data = response.json()

    results = data["results"]
    while data["has_more"] and get_all:
        payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
        url = f"https://api.notion.com/v1/databases/{databaseID}/query"
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        results.extend(data["results"])

    return results


def get_pages_with_filter(databaseID: str, filter: dict, num_pages=None):
    """
    If num_pages is None, get all pages, otherwise just the defined number.
    """
    url = f"https://api.notion.com/v1/databases/{databaseID}/query"

    get_all = num_pages is None
    page_size = 100 if get_all else num_pages

    payload = {"page_size": page_size, "filter": filter}
    response = requests.post(url, json=payload, headers=headers)

    data = response.json()

    results = data["results"]
    while data["has_more"] and get_all:
        payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
        url = f"https://api.notion.com/v1/databases/{databaseID}/query"
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        results.extend(data["results"])

    return results


def data(id):
    return {
        "Name": {
            "title": [
                {
                    "text": {
                        "content": TODO_MESSAGE
                    }
                }
            ]
        },
        "PERSON": {
            "relation": [
                {"id": id.__str__()}
            ]
        }
    }


active_filter = {
    "property": "Status",
    "select": {
        "equals": "Aktiv 🏃🏼‍♂️"
    }
}


def getMemberIDS():
    pages = get_pages_with_filter(MEMBERS_DATABASE, active_filter)

    ids = []

    for page in pages:
        page_id = page["id"]

        ids.append(page_id)
    return ids




ids = getMemberIDS()
threads = []
# create threads
for id in ids:
    print("Creating thread with id " + id.__str__() + "...")
    threads.append(threading.Thread(target=create_page, args=(
        data(id), TODOS_DATABASE)))
# start all threads
for x in threads:
    print("Starting thread " + x.__str__() + "...")
    x.start()
# Wait for all threads to finish then print a message
for x in threads:
    print("Waiting for thread " + x.__str__() + " to finish...")
    x.join()
print("Done!")

