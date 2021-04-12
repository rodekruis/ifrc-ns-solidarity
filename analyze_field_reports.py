import pandas as pd
import numpy as np
import os
from google.cloud import language_v1
from google.cloud import translate_v2 as translate
from apiclient import discovery
from google.oauth2 import service_account
import preprocessor as tp
from time import sleep
from requests.exceptions import ReadTimeout, ConnectionError
from country_list import countries_for_language
countries = dict(countries_for_language('en'))
from fuzzywuzzy import fuzz
from tqdm import tqdm
tqdm.pandas()

# get Google API credentials
TYPE_ = language_v1.Document.Type.PLAIN_TEXT
ENCODING_ = language_v1.EncodingType.UTF8
credentials = service_account.Credentials.from_service_account_file('ifrc-ns-covid-service-account.json')
translate_client = translate.Client(credentials=credentials)
nlp_client = language_v1.LanguageServiceClient(credentials=credentials)
df_demonyms = pd.read_csv('demonyms.csv', names=['demonym', 'country'])
demonym_dict = pd.Series(df_demonyms.country.values,index=df_demonyms.demonym).to_dict()
df_fdrs = pd.read_excel('donor_receiver_2019.xlsx', sheet_name='country_codes_2019', index_col=0)
df_fdrs.country = df_fdrs.country.str.lower()
fdrs_dict = pd.Series(df_fdrs.KPI_DON_Code.values,index=df_fdrs.country).to_dict()


def translate_to_english(row):
    text = row['PNS_action_summary']
    try:
        result = translate_client.translate(text, target_language="en")
    except ReadTimeout or ConnectionError:
        sleep(60)
        try:
            result = translate_client.translate(text, target_language="en")
        except ReadTimeout or ConnectionError:
            sleep(60)
            result = translate_client.translate(text, target_language="en")
    trans = result["translatedText"]
    return trans


def preprocess_text(row):
    text = row['PNS_action_summary_en']
    text = text.lower()
    text = text.replace(' rc', '')
    text = text.replace('red cross', '')
    text = text.replace('cruz roja', '')
    text = text.replace('croix rouge', '')
    text = text.replace('croix-rouge', '')
    text = text.replace(' cr ', ' ')
    return text


def analyze_entities(row):
    text = row['PNS_action_summary_en_clean']
    # Available types: PLAIN_TEXT, HTML
    type_ = language_v1.Document.Type.PLAIN_TEXT
    # Optional. If not specified, the language is automatically detected.
    # For list of supported languages:
    # https://cloud.google.com/natural-language/docs/languages
    language = "en"
    document = {"content": text, "type_": type_, "language": language}
    # Available values: NONE, UTF8, UTF16, UTF32
    encoding_type = language_v1.EncodingType.UTF8

    response = nlp_client.analyze_entities(request = {'document': document, 'encoding_type': encoding_type})
    locations = []
    for entity in response.entities:
        if language_v1.Entity.Type(entity.type_).name == "LOCATION":
            for mention in entity.mentions:
                locations.append(mention.text.content)
    return locations


def match_countries(row):
    location_entities = row['PNS_location_entities']
    location_entities = list(set(location_entities))
    countries_match = []
    for locaction_entity in location_entities:
        for demonym in demonym_dict.keys():
            if fuzz.ratio(locaction_entity.lower(),demonym.lower()) > 90:
                countries_match.append(demonym_dict[demonym])
        for country in demonym_dict.values():
            if fuzz.ratio(locaction_entity.lower(),country.lower()) > 90:
                countries_match.append(country)
    return list(set(countries_match))


def extract_fdrs(row):
    countries = row['PNS_countries']
    fdrs_match = []
    for country in countries:
        if country.lower() in fdrs_dict.keys():
            fdrs_match.append(fdrs_dict[country.lower()])
        else:
            print(f"{country} NOT FOUND")
    return fdrs_match


dir = 'data/field_reports_baseline'
data = 'field_reports.csv'
df_field_reports = pd.read_csv(f"{dir}/{data}")
print(df_field_reports.head())
df_field_reports_raw = df_field_reports.copy()
df_field_reports_raw = df_field_reports_raw.dropna(subset=['fdrs_report', 'fdrs_target'])
df_field_reports = df_field_reports.dropna(subset=['PNS_action_summary'])

# translate to english
print('translating to english')
df_field_reports['PNS_action_summary_en'] = df_field_reports.progress_apply(translate_to_english, axis=1)
df_field_reports['PNS_action_summary_en_clean'] = df_field_reports.progress_apply(preprocess_text, axis=1)
df_field_reports['PNS_location_entities'] = df_field_reports.progress_apply(analyze_entities, axis=1)
df_field_reports['PNS_countries'] = df_field_reports.progress_apply(match_countries, axis=1)
df_field_reports['PNS_FDRS'] = df_field_reports.progress_apply(extract_fdrs, axis=1)
print(df_field_reports.head())
df_field_reports.to_csv(f"{dir}/field_reports_parsed.csv", index=False)

df_adjacency = pd.DataFrame(0, index=fdrs_dict.values(), columns=fdrs_dict.values())

for ix, row in df_field_reports_raw.iterrows():
    if row['fdrs_report'] != row['fdrs_target']:
        df_adjacency.at[row['fdrs_report'], row['fdrs_target']] = 1
        df_adjacency.at[row['fdrs_target'], row['fdrs_report']] = 1

for ix, row in df_field_reports.iterrows():
    if len(row['PNS_FDRS']) == 0:
        continue
    for fdrs in row['PNS_FDRS']:
        if row['fdrs_report'] != fdrs:
            df_adjacency.at[row['fdrs_report'], fdrs] = 1
            df_adjacency.at[fdrs, row['fdrs_report']] = 1
df_adjacency = df_adjacency.fillna(0)
df_adjacency.to_csv(f"{dir}/adjacency_matrix_field_reports.csv")



