import numpy as np
import nltk
import time
import string
import asyncio

from geopy.adapters import AioHTTPAdapter
import geopy.geocoders as geocoders
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nrclex import NRCLex

from core.cleaner import stripFillerWords

nltk.download("punkt")
nltk.download("vader_lexicon")

timeout = 100

nom = geocoders.Nominatim(
    timeout=timeout,
    user_agent="bristol_geo_sentiment_analysis_project",
    adapter_factory=AioHTTPAdapter,
)

arc = geocoders.ArcGIS(
    timeout=timeout,
    adapter_factory=AioHTTPAdapter,
)

bing = geocoders.Bing(
    "AjFp_gjCldIwKBM50GFJNbIDP1nZdvDgqGHDBN3rU9Ro7-OUoV0mEmk3OkMi5brF",
    timeout=timeout,
    adapter_factory=AioHTTPAdapter,
)


async def nomanatim_call(address):
    result = {"lat": None, "long": None, "city": None, "country_code": None}
    location = await nom.geocode(address, exactly_one=True, addressdetails=True)
    if location:
        result["lat"] = location.latitude
        result["long"] = location.longitude

        if "address" in location.raw:
            if "city" in location.raw["address"]:
                result["city"] = location.raw["address"]["city"]
            if "country_code" in location.raw["address"]:
                result["country_code"] = location.raw["address"]["country_code"]

    return result


async def arc_call(address):
    result = {"lat": None, "long": None, "city": None, "country_code": None}
    location = await arc.geocode(
        address, exactly_one=True, out_fields=["City", "Country", "CountryCode"]
    )
    if location:
        result["lat"] = location.latitude
        result["long"] = location.longitude

        if "attributes" in location.raw:
            if "City" in location.raw["attributes"]:
                result["city"] = location.raw["attributes"]["City"]
            if "CountryCode" in location.raw["attributes"]:
                result["country_code"] = location.raw["attributes"]["CountryCode"]

    return result


async def bing_call(address):
    result = {"lat": None, "long": None, "city": None, "country_code": None}
    location = await bing.geocode(
        address, exactly_one=True, include_neighborhood=True, include_country_code=True
    )
    if location:

        if "address" in location.raw:
            if "locality" in location.raw["address"]:
                result["city"] = location.raw["address"]["locality"]
            if "countryRegionIso2" in location.raw["address"]:
                result["country_code"] = location.raw["address"]["countryRegionIso2"]

    return result


geo_funcs = [nomanatim_call, arc_call, bing_call]
rate_limit = 1  # Time to async sleep for each source after a call
num_geolocator_agents = len(geo_funcs)


def create_emotions(df, text_column_name):
    emotions = ["emotion_1", "emotion_2", "emotion_3"]

    # Add in the new emotion columns:
    for emotion in emotions:
        df[emotion] = np.nan

    def analyze_emotions(row):
        # Analyse and add the emotions of the row:
        analyzer = NRCLex(text=row[text_column_name])
        for index, emotion in enumerate(emotions):
            # If not enough emotions in the list, leave column as NaN:
            if len(analyzer.top_emotions) <= index:
                break
            row[emotion] = analyzer.top_emotions[index]

        return row

    df = df.apply(analyze_emotions, axis=1)

    return df


def create_bias(df, text_column_name):
    # Uses nltk vader to calc positive, negative, neutrality and compound columns

    fields = ["pos", "neg", "neu", "compound"]

    # Setup the new columns:
    for field in fields:
        df[field] = np.nan

    sia = SentimentIntensityAnalyzer()

    def analyze_bias(row):
        nonlocal sia

        results = sia.polarity_scores(row[text_column_name])

        for field in fields:
            row[field] = results[field]

        return row

    df = df.apply(analyze_bias, axis=1)

    return df


def create_cleaned(df, text_column_name):
    fields = ["cleaned_words"]
    for field in fields:
        df[field] = np.nan

    def clean(row):

        text = row[text_column_name]
        # First remove punctuation:
        text = text.translate(str.maketrans("", "", string.punctuation))

        # Split text into words:
        words = text.split()

        # Remove filler words:
        cleaned_words = stripFillerWords(words)

        row["cleaned_words"] = cleaned_words

        return row

    df = df.apply(clean, axis=1)

    return df


def create_geo(df, address_column_name):
    assert address_column_name in df, (df.columns, address_column_name)

    rows_parsed = 0
    no_of_rows = df.shape[0]

    if "index" not in df:
        df.reset_index(inplace=True)

    indexes_needing_parsing = df["index"].values.tolist()
    # Split the indexes between the agents:
    # agent_index_splits = np.array_split(indexes, num_geolocator_agents)

    fields = ["lat", "long", "city", "country_code"]

    async def parse_addresses(geo_func):
        nonlocal df
        nonlocal rows_parsed
        nonlocal no_of_rows
        nonlocal fields

        last_call_time = 0
        while indexes_needing_parsing:
            index = indexes_needing_parsing.pop(0)

            address = df.iloc[index][address_column_name]

            # Only doing if valid string address:
            if type(address) == str:
                time_since_last_call = time.time() - last_call_time

                # To prevent throttling limit call rate to rate_limit seconds:
                if time_since_last_call < rate_limit:
                    await asyncio.sleep(rate_limit - time_since_last_call)

                result = await geo_func(address)
                last_call_time = time.time()

                for field in fields:
                    assert field in result, result

                    if result[field]:
                        df.at[index, field] = result[field]

                await asyncio.sleep(rate_limit)

            rows_parsed += 1
            print("{}/{} addresses parsed.".format(rows_parsed, no_of_rows))

    # Adds in the lat long, city and country for the geo information if readable
    print("Parsing geo info...")

    for field in fields:
        df[field] = np.nan

    tasks = [parse_addresses(func) for func in geo_funcs]
    asyncio.get_event_loop().run_until_complete(asyncio.gather(*tasks))

    return df
