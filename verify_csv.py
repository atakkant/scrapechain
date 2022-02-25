import pandas as pd

file_path = "scrapechain/csv/solscan_2022-02-20 02:26:57.csv"


df = pd.read_csv(file_path,encoding='latin-1')

print(df.head())
empty_cells = []
print("number of rows: %d"%df.shape[0])
print("number of columns: %d"%df.shape[1])
