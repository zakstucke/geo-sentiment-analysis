#get tweets related to fake news hashtag

#HYPOTHESIS: People's sentiment in tweets has become increasingly mild as a reaction to rises/falls in cases/deaths over the past two years
#Country Basis plot the days case level alongside average sentiment per day/week/month

import pandas as pd
import json
import matplotlib.pyplot as plt
import pycountry
from scipy.stats import pearsonr

pd.options.mode.chained_assignment = None  # default='warn' this is needed for false positives warnings on reassigning pd dataframe

#TWEET DATA FROM PREPROCESSED DF
with open("./processed_data/final_df.json", "r") as file:
    COVIDdf = pd.read_json(json.load(file))

#print(COVIDdf.head(20))
#lookup iso-3 country code
def normaliseCC(row):
    code = row['country_code']
    iso3 = pycountry.countries.get(alpha_2=code)
    if iso3:
        return iso3.alpha_3
    else:
        return code

def cleanTweetDF(df):
    df = COVIDdf[COVIDdf["country_code"].notna()]
    df = df[df["date"].notna()]
    df['iso_code'] = df.apply(lambda row : normaliseCC(row), axis=1) #normalise country codes to standard iso where exists
    return df[['iso_code', 'text', 'date']].copy()





# def groupDFByMonth(iso_col_name, code, df):
#     isCountry = df[iso_col_name]==code
#     df = df[isCountry]
#     dates = pd.to_datetime(df['date'])
#     df['date'] = dates
#     df = df.set_index('date')
#     return df.groupby(pd.Grouper(freq='M')).mean()


for i in COVIDdf['text']:
    if "infertility" in i.lower():
        print(i)