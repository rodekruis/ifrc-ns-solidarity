import networkx as nx
import pandas as pd

# # load baseline adjacency matrix
# df_baseline_1 = pd.read_excel('donor_receiver_2019.xlsx', sheet_name='donor_2019', index_col=0)
# print(df_baseline_1.head())
# df_baseline_1 = df_baseline_1.astype(int)
# df_baseline_2 = pd.read_excel('donor_receiver_2019.xlsx', sheet_name='receiver_2019', index_col=0)
# df_baseline_2 = df_baseline_2.astype(int)
# for ix, row in df_baseline_2.iterrows():
#     for col in row.keys():
#         if row[col] > 0:
#             df_baseline_1.at[ix, row[col]] = row[col]
#
# G_baseline = nx.convert_matrix.from_pandas_adjacency(df_baseline_1)
# print(nx.info(G_baseline))
# G_baseline_degree = nx.degree_histogram(G_baseline)
# G_baseline_degree_sum = [a * b for a, b in zip(G_baseline_degree, range(0, len(G_baseline_degree)))]
# print('average degree: {}'.format(sum(G_baseline_degree_sum) / G_baseline.number_of_nodes()))

dir = 'data/projects_baseline'
df_covid = pd.read_csv(f"{dir}/adjacency_matrix_projects.csv", index_col=0)
G_covid = nx.convert_matrix.from_pandas_adjacency(df_covid)
print(nx.info(G_covid))
G_covid_degree = nx.degree_histogram(G_covid)
G_covid_degree_sum = [a * b for a, b in zip(G_covid_degree, range(0, len(G_covid_degree)))]
# if G_covid.number_of_nodes() > G_baseline.number_of_nodes():
#     print('WARNING: more countries in field reports, calculating degree centrality with baseline value')
#     print('average degree: {}'.format(sum(G_covid_degree_sum) / G_baseline.number_of_nodes()))
# else:
print('average degree: {}'.format(sum(G_covid_degree_sum) / G_covid.number_of_nodes()))

dir = 'data/projects_covid'
df_covid = pd.read_csv(f"{dir}/adjacency_matrix_projects.csv", index_col=0)
G_covid = nx.convert_matrix.from_pandas_adjacency(df_covid)
print(nx.info(G_covid))
G_covid_degree = nx.degree_histogram(G_covid)
G_covid_degree_sum = [a * b for a, b in zip(G_covid_degree, range(0, len(G_covid_degree)))]
print('average degree: {}'.format(sum(G_covid_degree_sum) / G_covid.number_of_nodes()))