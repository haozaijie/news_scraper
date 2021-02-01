import datetime

from src.base_spider import Cnn, Wsj
from src.clean import clean_data, get_daily_count, select_weekday
from src.sentiment import analyze_sentiment, plot_sentiment

SOURCES = ['CNN', 'WSJ']

def main(topic, start_date, end_date):
    # scrape data from web
    cnn_scraper = Cnn(topic)
    cnn_scraper.write_file()

    wsj_scraper = Wsj(topic)
    wsj_scraper.write_file()

    # clean data and get daily count
    combined = clean_data((topic))

    combined = combined.loc[(combined['date'] >= start_date) & (combined['date'] <= end_date),:]

    combined.to_csv(f"files/combined_{topic}.csv", index=False)
    daily_count = get_daily_count(combined)
    daily_count.to_csv(f"files/daily_count_{topic}.csv", index=False)

    # plot daily count
    plot_sentiment(daily_count,
                   SOURCES,
                   "number of news published daily by source",
                   "daily_count")

    # run sentiment analysis on cleaned data
    df_sentiment, df_sentiment_by_source_tag, df_sentiment_by_source = analyze_sentiment(combined)
    for df in [df_sentiment, df_sentiment_by_source_tag, df_sentiment_by_source]:
        df =  df.loc[df['date'].apply(select_weekday)].sort_values(['date'])
    df_sentiment.to_csv("files/sentiment_raw.csv")
    df_sentiment_by_source_tag.to_csv("files/df_sentiment_by_source_tag.csv")
    df_sentiment_by_source.to_csv("files/df_sentiment_by_source.csv")

    # plot polarity and subjectivity by source
    for measure in ['polarity', 'subjectivity']:
        plot_sentiment(df_sentiment_by_source,
                       [f'weighted_{measure}_CNN',f'weighted_{measure}_WSJ'],
                       f"{measure.title()} by source",
                       f"{measure}_by_source")
    print("polarity and subjectivity by source plots generated")

    # plot polarity and subjectivity comparision
    for source in SOURCES:
        plot_sentiment(df_sentiment_by_source,
                       [f'weighted_polarity_{source}',f'weighted_subjectivity_{source}'],
                       f"Polarity and subjectivity of {source}",
                       f"polarity_subjectivity_{source}")
    print("polarity and subjectivity comparision plots generated")


if __name__ == "__main__":
    topic = input("what news topic are you interested in?\n").strip()
    start_date = input("start date (in yyyy-mm-dd format)\n").strip()
    end_date = input("end date (in yyyy-mm-dd format)\n").strip()
    main(topic, start_date, end_date)
