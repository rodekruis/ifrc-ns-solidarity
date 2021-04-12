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
action = ["api", "v2", "project", "list"]
params = {
    "limit": 10000,
}
results = client.action(schema, action, params=params)
ids = [field_report["id"] for field_report in results["results"]]
print(results["count"], len(ids))

df_baseline = pd.DataFrame()
df_covid = pd.DataFrame()

for id in ids:
    results = requests.get(f"https://goadmin.ifrc.org/api/v2/project/{id}/?id={id}", headers=headers).json()
    # print(results)
    try:
        country_iso_reporting = results["reporting_ns_detail"]["iso3"]
        country_fdrs_reporting = results["reporting_ns_detail"]["fdrs"]
        country_iso_target = results["project_country_detail"]["iso3"]
        country_fdrs_target = results["project_country_detail"]["fdrs"]
        secondary_sectors_display = ""
        if "secondary_sectors_display" in results.keys():
            if len(results["secondary_sectors_display"])>0:
                secondary_sectors_display =', '.join(results["secondary_sectors_display"])
        start_date = results["start_date"]
        end_date = results["end_date"]
        name = results["name"]

        if 'covid' in secondary_sectors_display.lower() or 'covid' in name.lower():
            df_covid = df_covid.append(pd.Series({"country_iso_reporting": country_iso_reporting,
                                      "id": id,
                                      "country_fdrs_reporting": country_fdrs_reporting,
                                      "country_iso_target": country_iso_target,
                                      "country_fdrs_target": country_fdrs_target,
                                      "secondary_sectors_display": secondary_sectors_display,
                                      "start_date": start_date,
                                      "end_date": end_date,
                                      "name": name}), ignore_index=True)
        else:
            df_baseline = df_baseline.append(pd.Series({"country_iso_reporting": country_iso_reporting,
                                                  "id": id,
                                                  "country_fdrs_reporting": country_fdrs_reporting,
                                                  "country_iso_target": country_iso_target,
                                                  "country_fdrs_target": country_fdrs_target,
                                                  "secondary_sectors_display": secondary_sectors_display,
                                                  "start_date": start_date,
                                                  "end_date": end_date,
                                                  "name": name}), ignore_index=True)
        print(len(df_covid), len(df_baseline))
    except:
        continue

print(df_covid.head())
print(df_baseline.head())
df_covid.to_csv('data/projects_covid/projects.csv', index=False)
df_baseline.to_csv('data/projects_baseline/projects.csv', index=False)