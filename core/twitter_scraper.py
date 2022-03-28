import pandas as pd
import requests
import math
from requests.models import PreparedRequest

TOKEN_TWITTER = "Bearer AAAAAAAAAAAAAAAAAAAAAPT%2FNAEAAAAAwK6N9D%2FcN4TCGS34qJp5qtjNXp8%3DxFovyPVqTPMgBJkVFCgpGapuoFwLXt7aEFFUJc0tTac8FNQ0Rn"

# Only from last 7 days
RECENT_TWEETS_URL = "https://api.twitter.com/2/tweets/search/recent"
TWEET_BY_ID_URL = "https://api.twitter.com/2/tweets?"
MAX_TWEETS_PER_CALL = 100

# Would require applying for an academic licence key (currently only have standard)
# ALL_TWEETS_URL = "https://api.twitter.com/2/tweets/search/all"


def get_chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


# Merges obj2 into obj1
def merge_dicts(obj1, obj2):
    assert type(obj1) == dict and type(obj2) == dict

    for key in obj2:
        if key not in obj1:
            obj1[key] = obj2[key]
        else:
            assert type(obj1[key]) == type(
                obj2[key]
            ), "Why do the types not match if they have the same key? Key: {}".format(key)

            if type(obj1[key]) == dict:
                obj1[key] = merge_dicts(obj1[key], obj2[key])
            elif type(obj1[key]) == list:
                obj1[key] += obj2[key]
            else:
                raise Exception(
                    "Obj1 and 2 have key values which aren't list or dict that are trying to be merged, key: {}".format(
                        key
                    )
                )

    return obj1


class TwitterScraper:
    def __init__(self):
        pass

    def _get_tweets_by_id(self, ids):
        params = {
            "ids": ids,
            "tweet.fields": "text,geo,lang,public_metrics,created_at",
            "expansions": "author_id,geo.place_id",
            "user.fields": "location",
            "place.fields": "contained_within,country,country_code,full_name,geo,id,name,place_type",
        }

        req = PreparedRequest()
        req.prepare_url(TWEET_BY_ID_URL, params)

        response = requests.get(req.url, headers={"Authorization": TOKEN_TWITTER})
        return response.json()

    def _get_recent_tweets(self, query, next_token=None):

        # https://developer.twitter.com/en/docs/twitter-api/tweets/search/quick-start/recent-search

        params = {
            "query": query,
            "tweet.fields": "text,created_at,possibly_sensitive,geo,lang,public_metrics",
            "expansions": "author_id,geo.place_id,referenced_tweets.id",
            "user.fields": "created_at,description,location",
            "place.fields": "contained_within,country,country_code,full_name,geo,id,name,place_type",
            "max_results": str(
                MAX_TWEETS_PER_CALL
            ),  # Default is 10 MAX_TWEETS_PER_CALL is max allowed
        }

        if next_token:
            params["next_token"] = next_token

        req = PreparedRequest()
        req.prepare_url(RECENT_TWEETS_URL, params)

        response = requests.get(req.url, headers={"Authorization": TOKEN_TWITTER})

        return response.json()

    def get_recent_tweets(self, query, max_tweets_about=1000):
        next_token = None

        data = {}

        # Call the number of times required to get max_tweets_about:
        total_pages = math.ceil(max_tweets_about / MAX_TWEETS_PER_CALL)

        for x in range(total_pages):
            print("Pulling page {}/{} of tweets...".format(x + 1, total_pages))
            new_data = self._get_recent_tweets(query, next_token=next_token)

            meta = new_data["meta"]
            del new_data["meta"]

            # Concat the new info into the data obj:
            data = merge_dicts(data, new_data)

            # Setup the token so the next call pulls the next "page" of tweets:
            next_token = meta["next_token"]

            if meta["result_count"] < MAX_TWEETS_PER_CALL:
                # No more tweets from twitter available so stop calling:
                break

        return data

    def get_tweets_by_ids(self, tweet_ids):
        max_per_call = 100

        data = {}
        chunks = list(get_chunks(tweet_ids, max_per_call))
        no_of_chunks = len(chunks)

        print("Pulling tweet data...")
        for index, tweet_id_chunk in enumerate(chunks):
            print("Call: {}/{}".format(index + 1, no_of_chunks))
            new_data = self._get_tweets_by_id(",".join(tweet_id_chunk))

            if "errors" in new_data:
                del new_data["errors"]
            data = merge_dicts(data, new_data)
        print("Finished pulling tweets!")

        print("Parsing tweet data...")
        # Tweets in "data", user data in "includes": "users", place data in "includes": "places"

        tweets = data["data"]
        users = data["includes"]["users"]
        places = data["includes"]["places"]

        # Add user information to each tweet:
        for user in users:
            for tweet in tweets:
                if "author_id" in tweet and user["id"] == tweet["author_id"]:
                    if "name" in user:
                        tweet["author_name"] = user["name"]
                    if "username" in user:
                        tweet["author_username"] = user["username"]
                    if "location" in user:
                        tweet["author_location"] = user["location"]

        # Add place information to each tweet:
        for place in places:
            for tweet in tweets:
                if (
                    "geo" in tweet
                    and "place_id" in tweet["geo"]
                    and place["id"] == tweet["geo"]["place_id"]
                ):
                    if "full_name" in place:
                        tweet["geo"]["full_name"] = place["full_name"]

        return pd.json_normalize(tweets)
