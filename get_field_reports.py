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
action = ["api", "v2", "field_report", "list"]
params = {
    "limit": 10000,
    "is_covid_report": False,
}
results = client.action(schema, action, params=params)
ids = [field_report["id"] for field_report in results["results"]]
print(results["count"], len(ids))

df = pd.DataFrame()

for id in ids:
    results = requests.get(f"https://goadmin.ifrc.org/api/v2/field_report/{id}/?id={id}", headers=headers).json()
    # print(results)
    try:
        country_iso_user = results["user"]["profile"]["country"]["iso3"]
        country_fdrs_user = results["user"]["profile"]["country"]["fdrs"]
        NS_user = results["user"]["profile"]["country"]["society_name"]
        countries_iso_report, countries_fdrs_report = [], []
        for country in results["countries"]:
            countries_iso_report.append(country["iso3"])
            countries_fdrs_report.append(country["fdrs"])

        PNS_action_summary = ""
        if "actions_taken" in results.keys():
            for action in results["actions_taken"]:
                if "organization" in action.keys() and "summary" in action.keys():
                    if action["organization"] == "PNS":
                        PNS_action_summary = action["summary"]

        for iso, fdrs in zip(countries_iso_report, countries_fdrs_report):
            df = df.append(pd.Series({"iso_report": country_iso_user,
                                      "id": id,
                                      "fdrs_report": country_fdrs_user,
                                      "iso_target": iso,
                                      "fdrs_target": fdrs,
                                      "PNS_action_summary": PNS_action_summary}), ignore_index=True)
    except:
        continue

print(df.head())
df.to_csv('data/field_reports_baseline/field_reports.csv', index=False)