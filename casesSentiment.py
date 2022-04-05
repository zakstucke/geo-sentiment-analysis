#HYPOTHESIS: People's sentiment in tweets has become increasingly mild as a reaction to rises/falls in cases/deaths over the past two years
#Country Basis plot the days case level alongside average sentiment per day/week/month

import pandas as pd
import json
import matplotlib.pyplot as plt
import pycountry
from scipy.stats import pearsonr

pd.options.mode.chained_assignment = None  # default='warn' this is needed for false positives warnings on reassigning pd dataframe

#CASES DATA FROM CSV
WHOfile = "data/WHO_covid_data_by_COUNTRY.csv"
WHOdf = pd.read_csv(WHOfile, usecols=["iso_code", "date", "new_cases"])

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
    return df[['iso_code', 'compound', 'date']].copy()

def groupDFByMonth(iso_col_name, code, df):
    isCountry = df[iso_col_name]==code
    df = df[isCountry]
    dates = pd.to_datetime(df['date'])
    df['date'] = dates
    df = df.set_index('date')
    return df.groupby(pd.Grouper(freq='M')).mean()

def plot(WHOdf, COVIDdf, iso_code):
    whoiso = groupDFByMonth("iso_code", iso_code, WHOdf)
    covidiso = groupDFByMonth("iso_code", iso_code, COVIDdf)

    title = iso_code + " Avg Daily New Cases By Month over Covid with Average Sentiment of Tweets Regarding COVID"
    whoiso.join(covidiso)
    df = pd.merge(whoiso, covidiso, left_index=True, right_index=True)
    df = df.reset_index()

    fig, ax = plt.subplots(figsize=(10,5))

    ax.plot(df.date, df.new_cases, color='red')
    ax.set_xlabel("Date")
    ax.set_ylabel("New Cases", color="red")
    ax.set_title(title)

    ax2 = ax.twinx()
    ax2.plot(df.date, df.compound, color='blue')
    ax2.set_ylabel("Average Sentiment", color='blue')

    #Conduct hypothesis test at 5% significance level
    p, corr, result = hypothesisTest(df.new_cases, df.compound, 0.05)
    plt.text(min(df.date),max(df.compound),"Correlation: " + str(corr), fontsize=13)

    plt.show()

def hypothesisTest(x, y, alpha):
    likelyDependent = False
    corr, p = pearsonr(x, y)
    #print('Correlation=%.3f, p=%.3f' % (corr, p))
    if p < alpha:
	       likelyDependent = True
    return p, corr, likelyDependent


COVIDdf = cleanTweetDF(COVIDdf)

#ENTER ANY COUNTRY CODE (SOME HAVE MORE TWEETS THAN OTHERS SO WILL SHOW BETTER RESULTS)
plot(WHOdf, COVIDdf, "RUS")
plot(WHOdf, COVIDdf, "USA")
plot(WHOdf, COVIDdf, "DEU")
plot(WHOdf, COVIDdf, "CAN")
