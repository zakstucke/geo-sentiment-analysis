import os
import json
import time
import pandas as pd
import numpy as np
import pycountry
import linecache

# from core.twitter_scraper import TwitterScraper
from core.sentiment_analysis import (
    create_df,
    analyze_bias,
    analyze_emotions,
    clean_row_text,
    apply_geo,
)
from core.twitter_scraper import TwitterScraper


# from core.scraper import fetchTweet
pd.set_option("display.max_rows", 50)
pd.set_option("display.max_columns", 50)


def extract_csv_subset(save_filepath, subset_size, file_subset=None):
    print("Extracting subset size of: {} from raw csv...".format(subset_size))

    # Have split the datasets into small chunks to help with memory issues:
    basepath = os.path.join(".", "datasets", "chunks")

    files = [f for f in os.listdir(basepath) if os.path.isfile(os.path.join(basepath, f))]
    if file_subset:
        files = files[:file_subset]
    total_files = len(files)

    # First get the total number of rows
    start_index = 0
    total_rows = 0
    files_info = []
    for index, filename in enumerate(files):
        with open(os.path.join(basepath, filename), "r") as file:
            count = sum(1 for _ in file)
            count -= 1  # For the header of the csv
            files_info.append(
                {
                    "name": filename,
                    "total_rows": count,
                    "start_index": start_index,
                    "end_index": start_index + count,
                    "indexes": [],
                }
            )
            start_index += count

        print("{}/{} files processed.".format(index + 1, total_files))

    total_rows = sum(file_info["total_rows"] for file_info in files_info)
    indexes = [int(val) for val in np.linspace(0, total_rows - 1, num=subset_size)]

    # Assign the indexes to each group:
    current_file_index = 0
    for index in indexes:
        assert files_info[current_file_index]["start_index"] <= index
        while files_info[current_file_index]["end_index"] <= index:
            current_file_index += 1
        files_info[current_file_index]["indexes"].append(index)

    completed = 0
    with open(save_filepath, "w") as file:
        file.write("tweet_id,date,time,lang,country_place\n")

    for file_info in files_info:
        path = os.path.join(basepath, file_info["name"])
        offset = file_info["start_index"]
        with open(save_filepath, "a") as file:  # Appending
            for index in file_info["indexes"]:
                file.write(
                    linecache.getline(path, index + 2 - offset)
                )  # +2 as one for index to line, one for skipping header row
                completed += 1
        linecache.clearcache()
        print("{}/{} rows parsed.".format(completed, subset_size))

    return True


def create_tweet_csv(raw_csv_subset, tweet_csv_filepath):
    with open(raw_csv_subset, "r") as file:
        raw_df = pd.read_csv(file)

    tweets_ids = raw_df["tweet_id"].astype("string").values

    # Scrape all the tweets and save to csv: (handles crashes and continuations)
    TwitterScraper().get_tweets_by_ids(tweets_ids, tweet_csv_filepath)


def process_final_df(tweet_csv_filename, save_filepath):
    with open(tweet_csv_filename, "r") as file:
        df = pd.read_csv(file, low_memory=False)

    cleaned_text_fields = ["cleaned_words"]
    emotion_fields = ["emotion_1", "emotion_2", "emotion_3"]
    sentiment_fields = ["pos", "neg", "neu", "compound"]
    geo_fields = ["iso_code", "country", "city", "lat", "lng"]

    # Adding in the new columns set to nan:
    df = create_df(df, emotion_fields + sentiment_fields + cleaned_text_fields + geo_fields)

    index = 0
    average_secs = 0
    total_rows = df.shape[0]

    def apply_all(row):
        nonlocal index
        nonlocal total_rows
        nonlocal average_secs

        before = time.time()

        row = clean_row_text(row)
        row = analyze_emotions(row, "text", emotion_fields)
        row = analyze_bias(row, "text", sentiment_fields)
        row = apply_geo(row)

        index += 1
        time_taken = time.time() - before
        average_secs = average_secs + ((time_taken - average_secs) / index)

        if index % 100 == 0:
            seconds_remaining = average_secs * (total_rows - index)
            print(
                "Rows processed: {}/{}. Estimated minutes remaining: {:0.2f}".format(
                    index, total_rows, seconds_remaining / 60
                )
            )

        return row

    print("Rows to process: {}".format(df.shape[0]))
    df = df.apply(apply_all, axis=1)

    # Make sure all Nones are Nans:
    df = df.fillna(value=np.nan)

    with open(save_filepath, "w") as file:
        json.dump(df.to_json(), file)

    return True


def read_final_df(filepath):
    with open(filepath, "r") as file:
        df = pd.read_csv(file)

    return df


def normaliseCC(row):
    code = row["country_code"]
    if code:
        iso3 = pycountry.countries.get(alpha_2=code)
        if iso3:
            return iso3.alpha_3
        else:
            return code
    else:
        return None


def main():
    raw_csv_subset_filepath = "./intermediary_non_commit_data/raw_csv_subset.txt"
    tweet_csv_filepath = "./intermediary_non_commit_data/tweet_csv.txt"
    final_output_csv_path = "./processed_data/final_csv.txt"
    subset_size = 1000000  # 1 million, will then drop after only including ones with addresses etc

    # extract_csv_subset(raw_csv_subset_filepath, subset_size)
    # create_tweet_csv(raw_csv_subset_filepath, tweet_csv_filepath)
    # process_final_df(tweet_csv_filepath, final_output_csv_path)
    df = read_final_df(final_output_csv_path)

    print(df.describe())
    print(df.shape)
    for x in range(10):
        print(df.iloc[x])


if __name__ == "__main__":
    main()
