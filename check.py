import pandas as pd

df = pd.read_excel("data.xlsx", header=None)

print(df.head(10))