import os
import datetime
import logging

import pandas as pd

FORMAT = "%(asctime)s - %(name)s - %(message)s"
logging.basicConfig(format=FORMAT)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def read(topic):
    file_list = []
    for source in ['CNN', 'WSJ']:
        if os.path.exists(f"files/{topic}_{source}_results.csv"):
            df_temp = pd.read_csv(f"files/{topic}_{source}_results.csv").drop_duplicates(subset=['headline'])
            df_temp['source'] = source
            file_list.append(df_temp)
    if file_list:
        return pd.concat(file_list, ignore_index=True)
    return None

def clean_date_string(value):
    try:
        if not value:
            value = pd.Timestamp(0)
        for min_string in [' min ago', ' mins ago', ' minutes ago']:
            if min_string in str(value):
                min = int(value.split(min_string)[0])
                value = pd.Timestamp.now() - datetime.timedelta(minutes=min)
        for hour_string in [' hour ago', ' hours ago']:
            if hour_string in str(value):
                hour = int(value.split(hour_string)[0])
                value = pd.Timestamp.now() - datetime.timedelta(hours=hour)

        value = pd.Timestamp(value)
        return pd.to_datetime(value.strftime("%Y-%m-%d"))
    except:
        logger.error(f"cannot convert {value} to  timestamp")
    

def clean_date(df):
    try:
        df['date'] = pd.to_datetime((df['date']))
    except:
        df['date'] = df['date'].apply(lambda row: clean_date_string(row))
    return df

def select_weekday(date_value):
    if date_value:
        if date_value.weekday() in [5,6]:
            return False
        return True
    return False

def clean_data(topic):
    combined = read(topic)
    if combined is not None:
        combined = clean_date(combined)
    return combined

def group_date(df):
    return df.resample("D", on ="date").count()['headline']

def get_daily_count(df, excl_weekend = False):

    daily_count = df.groupby('source').apply(group_date).unstack(0).fillna(0).reset_index().sort_values(['date'])
    if excl_weekend:
        daily_count = daily_count.loc[daily_count['date'].apply(select_weekday)].sort_values(['date'])
    
    logger.info("daily count file generated")
    return daily_count

def main(topic):
    logger.info(f'reading web crawler data to dataframe')
    combined = clean_data(topic)
    
    logger.info('CNN df head: \n%s', combined[combined.source=='CNN'].head()[['headline','date','source']])
    logger.info('WSJ df head: \n%s', combined[combined.source=='WSJ'].head()[['headline','date','source']])
    if not combined.empty:
        daily_count = get_daily_count(combined)
        daily_count.to_csv("files/daily_count.csv")

if __name__ == "__main__":
    main("coronavirus")
