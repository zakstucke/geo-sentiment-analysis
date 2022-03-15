import numpy as np
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nrclex import NRCLex

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
    fields = ["split_words","no_punctuation","no_filler"]
    for field in fields:
        df[field] = np.nan
    
    splitWords = cleaner.splitToWords(df)
    df["split_words"] = splitWords
    stripPunctuation = cleaner.stripPunctuation(splitWords)
    df["no_punctuation"] = stripPunctuation
    stripFillerWords = cleaner.stripFillerWords(stripPunctuation)
    df["no_filler"] = stripFillerWords
    return df

import pandas as pd
import cleaner
df = pd.DataFrame({"text": ["What a great day", "Today is awful", "I'm so happy", "Looking forward to a great day tomorrow.", "Yesterday was scary"]})
df = create_cleaned(df,"text")
print(df)
