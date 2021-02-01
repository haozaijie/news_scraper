from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('postgresql://haozaijie:password@localhost:5432/sample_db')

df = pd.read_csv('files/combined_coronavirus.csv')
df.to_sql('news_scraper.raw', engine, if_exists='replace', index=False)
