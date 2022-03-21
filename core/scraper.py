import pandas as pd
from core.twitter_scraper import TwitterScraper
import json

# whole dataset -> pandas frame
# data = pd.read_csv('covidvaccine.csv')

# available columns in covidvaccine.csv are: user_name,user_location,user_description,
#                       user_created,user_followers,user_friends,
#                       user_favourites,user_verified,date,text,
#                       hashtags,source,is_retweet

# import with only certain columns
def CSVTweetReader():
    df = pd.read_csv("covidvaccine.csv", usecols=["user_location", "date", "text"])
    return df


# takes tweet ids which can be from CSV and return tweet text and geo data
# input format id,id e.g fetchTweet("1261326399320715264,1278347468690915330")
# returns pd dataframe
def fetchTweet(ids):
    scraper = TwitterScraper()
    resObj = scraper._get_tweets_by_id(ids)
    df = pd.json_normalize(resObj, record_path=["data"])
    return df
