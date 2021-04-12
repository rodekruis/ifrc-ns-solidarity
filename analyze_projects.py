import pandas as pd
import numpy as np
import os
from time import sleep
from requests.exceptions import ReadTimeout, ConnectionError
from country_list import countries_for_language
countries = dict(countries_for_language('en'))
from fuzzywuzzy import fuzz
from tqdm import tqdm
tqdm.pandas()


dir = 'data/projects_covid'
data = 'projects.csv'
df_field_reports = pd.read_csv(f"{dir}/{data}")
print(df_field_reports.head())
df_field_reports = df_field_reports.dropna(subset=['country_fdrs_reporting', 'country_fdrs_target'])
fdrs = list(set(df_field_reports['country_fdrs_reporting'].to_list()+df_field_reports['country_fdrs_target'].to_list()))

df_adjacency = pd.DataFrame(0, index=fdrs, columns=fdrs)

for ix, row in df_field_reports.iterrows():
    if row['country_fdrs_reporting'] != row['country_fdrs_target']:
        df_adjacency.at[row['country_fdrs_reporting'], row['country_fdrs_target']] = 1
        df_adjacency.at[row['country_fdrs_target'], row['country_fdrs_reporting']] = 1

df_adjacency.to_csv(f"{dir}/adjacency_matrix_projects.csv")



