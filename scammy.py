import pandas as pd

df = pd.read_csv('scoredata_temp.csv')


print(df['snow'].sum())
