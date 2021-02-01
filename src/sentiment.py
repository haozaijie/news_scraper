import pandas as pd
from textblob import TextBlob
from matplotlib import pyplot as plt


def get_country_tag(row):
    US_LIST = ['US', 'AMERICA', 'UNITED STATES']
    CHINA_LIST = ['CHINA', 'CHINESE']
    US_TAG = [x for x in US_LIST if x in row.upper()]
    CHINA_TAG = [x for x in CHINA_LIST if x in row.upper()]
    if US_TAG and CHINA_TAG:
        return "CHINA_US"
    elif CHINA_TAG:
        return "CHINA"
    elif US_TAG:
        return "US"
    else:
        return None

# use textblob to get polarity and subjectivity
def get_polarity(val):
    return TextBlob(str(val)).sentiment.polarity

def get_subjectivity(val):
    return TextBlob(str(val)).sentiment.subjectivity

def get_sentiment(df):
    for column in ['headline', 'body']:
        df.loc[:,column + '_polarity']= df[column].apply(get_polarity)
        df.loc[:,column + '_subjectivity'] = df[column].apply(get_subjectivity)

    df.loc[:,'weighted_polarity'] = 0.5*df['headline_polarity'] + 0.5*df['body_polarity']
    df.loc[:,'weighted_subjectivity'] = 0.5*df['headline_subjectivity'] + 0.5*df['body_subjectivity']
    df.loc[:, 'date'] = pd.to_datetime(df['date'])

    output_columns = ['date', 'source', 'tag', 'weighted_polarity', 'weighted_subjectivity']

    return df[output_columns]


def get_mean(df):
    return df.set_index('date').resample('D').mean()


def sentiment_by_source_tag(df):
    group = df.groupby(['source','tag']).apply(get_mean)
    group = group.unstack([0,1])
    group.columns = ["_".join(col) for col in group.columns.values]
    return group

def sentiment_by_source(df):
    group = df.groupby(['source']).apply(get_mean)
    group = group.unstack(0)
    group.columns = ["_".join(col) for col in group.columns.values]
    return group

# def select_date_range(df, start_date, end_date):
#     # print(df.columns)
#     return df.loc[(df['date'] >= start_date) & (df['date'] <= end_date),:].sort_values(['date'])

def analyze_sentiment(df):
    df['tag'] = df['headline'].apply(get_country_tag)
    df_sentiment = get_sentiment(df)
    # print(df_sentiment.head())

    df_sentiment_by_source_tag = sentiment_by_source_tag(df_sentiment)
    df_sentiment_by_source = sentiment_by_source(df_sentiment)

    for df in [df_sentiment, df_sentiment_by_source_tag, df_sentiment_by_source]:
        df.reset_index(inplace=True)
        df.fillna(0, inplace=True)
        df.sort_values(['date'], inplace=True)

    return df_sentiment, df_sentiment_by_source_tag, df_sentiment_by_source

def plot_sentiment(df, columns, ylabel, pic_name):
    # print(df.dtypes)
    plt.style.use('seaborn')

    for col in columns:
        plt.plot_date(df['date'].dt.to_pydatetime(), df[col],
                      linestyle = 'solid',
                      linewidth = 2,
                      marker="o",
                      label = col)

    # plt.xticks(df['date'])
    plt.xlabel("Date")
    plt.ylabel(ylabel)
    plt.legend()

    plt.tight_layout()
    plt.savefig(f'files/{pic_name}.png')
    plt.close()


if __name__ == '__main__':
    topic = "coronavirus"
    df = pd.read_csv(f"combined_{topic}.csv")
    df_sentiment, df_sentiment_by_source_tag, df_sentiment_by_source =analyze_sentiment(df)
    df_sentiment.to_csv("sentiment_raw.csv")
    df_sentiment_by_source_tag.to_csv("df_sentiment_by_source_tag.csv")
    df_sentiment_by_source.to_csv("df_sentiment_by_source.csv")

    plot_sentiment(df_sentiment_by_source,
                   ['weighted_polarity_BBC','weighted_polarity_CNN','weighted_polarity_WSJ'],
                   "Polarity by source",
                   "polarity_by_source")
