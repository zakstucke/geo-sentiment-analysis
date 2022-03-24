import json
import random
import pandas as pd

# from core.twitter_scraper import TwitterScraper
from core.sentiment_analysis import create_emotions, create_bias, create_cleaned, create_geo
from core.twitter_scraper import TwitterScraper
from core.scraper import fetchTweet

pd.set_option("display.max_rows", 50)
pd.set_option("display.max_columns", 50)


def parse_raw_csv(filepath, save_filepath, subset=None):
    assert subset is None or type(subset) == int, subset

    if subset:
        # Getting a random subset of the dataset for quick processing:
        n = sum(1 for line in open(filepath)) - 1  # number of records in file (excludes header)
        s = subset  # desired sample size
        skip = sorted(
            random.sample(range(1, n + 1), n - s)
        )  # the 0-indexed header will not be included in the skip list
        df = pd.read_csv(filepath, skiprows=skip)
    else:
        df = pd.read_csv(filepath)

    with open(save_filepath, "w") as file:
        json.dump(df.to_json(), file)

    return True


def create_tweet_df(raw_df_filepath, output_filepath):
    with open(raw_df_filepath, "r") as file:
        raw_df = pd.read_json(json.load(file))

    tweets_ids = raw_df["tweet_id"].astype("string").values.tolist()
    # Scrape all the tweet ids:
    df = TwitterScraper().get_tweets_by_ids(tweets_ids)

    with open(output_filepath, "w") as file:
        json.dump(df.to_json(), file)


def process_final_df(tweet_df_filename, save_filepath):
    with open(tweet_df_filename, "r") as file:
        df = pd.read_json(json.load(file))

    df = create_cleaned(df, "text")
    df = create_bias(df, "text")
    df = create_emotions(df, "text")
    df = create_geo(df, "author_location")

    with open(save_filepath, "w") as file:
        json.dump(df.to_json(), file)

    return True


def read_final_df(filepath):
    with open(filepath, "r") as file:
        df = pd.read_json(json.load(file))

    return df


def main():
    raw_dataset_filepath = "./datasets/full_dataset_clean.csv"
    raw_df_filepath = "./processed_data/raw_df.json"
    tweet_df_filepath = "./processed_data/tweet_df.json"
    final_output_df_filepath = "./processed_data/final_df.json"

    # parse_raw_csv(raw_dataset_filepath, raw_df_filepath, subset=10000)
    # create_tweet_df(raw_df_filepath, tweet_df_filepath)
    # process_final_df(tweet_df_filepath, final_output_df_filepath)
    df = read_final_df(final_output_df_filepath)
    print(df.iloc[0])
    print(df.shape)


if __name__ == "__main__":
    main()
