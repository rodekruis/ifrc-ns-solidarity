import coreapi
import requests
import pandas as pd
import json

with open('go-api-token.json') as json_file:
    headers = json.load(json_file)

# Initialize a client & load the schema document
client = coreapi.Client()
schema = client.get("https://goadmin.ifrc.org/docs/")

# Interact with the API endpoint
action = ["api", "v2", "personnel_deployment", "list"]
params = {
    "limit": 10000,
    # "is_covid_report": False,
}
results = client.action(schema, action, params=params)
ids = [field_report["id"] for field_report in results["results"]]
print(results["count"], len(ids))