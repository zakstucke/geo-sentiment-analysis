import pandas as pd

# from core.twitter_scraper import TwitterScraper
from core.sentiment_analysis import create_emotions, create_bias, create_cleaned, create_geo

pd.set_option("display.max_rows", 50)
pd.set_option("display.max_columns", 50)


def main():
    # tweetScraper = TwitterScraper()

    # data = tweetScraper.get_recent_tweets("Ukraine", max_tweets_about=10)
    # singleTweet = cleaner.getSingleTweet(data)
    # print(singleTweet)
    # tweetTextList = cleaner.getText(data)
    # for tweet in tweetTextList:
    #    print(tweet)
    # cleanerTest()

    df = pd.read_csv("covidvaccine.csv", nrows=10)

    df = create_cleaned(df, "text")
    df = create_bias(df, "text")
    df = create_emotions(df, "text")
    df = create_geo(df, "user_location")

    print(df)


if __name__ == "__main__":
    main()
