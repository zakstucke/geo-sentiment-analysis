import numpy as np
import nltk
import string

from geopy.geocoders import Nominatim
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nrclex import NRCLex

from core.cleaner import stripFillerWords

nltk.download("punkt")
nltk.download("vader_lexicon")


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
    # Adds in the lat long, city and country for the geo information if readable

    fields = ["lat", "long", "city", "country", "country_code"]
    for field in fields:
        df[field] = np.nan

    geolocator = Nominatim(user_agent="bristol_geo_sentiment_analysis_project")

    def _create_geo(row):
        address = row[address_column_name]

        location = geolocator.geocode(address, exactly_one=True, addressdetails=True)
        if location:
            row["lat"] = location.latitude
            row["long"] = location.longitude

            if "address" in location.raw:
                if "city" in location.raw["address"]:
                    row["city"] = location.raw["address"]["city"]
                if "country" in location.raw["address"]:
                    row["country"] = location.raw["address"]["country"]
                if "country_code" in location.raw["address"]:
                    row["country_code"] = location.raw["address"]["country_code"]

        return row

    df = df.apply(_create_geo, axis=1)

    return df
