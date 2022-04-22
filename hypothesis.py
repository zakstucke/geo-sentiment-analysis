import pandas as pd
import json
import matplotlib.pyplot as plt
import pycountry
import datetime
from scipy.stats import pearsonr
import numpy as np

pd.options.mode.chained_assignment = None  # default='warn' this is needed for false positives warnings on reassigning pd dataframe

WHOfile = "data/WHO_covid_data_by_COUNTRY.csv"
WHOdf = pd.read_csv(WHOfile, usecols=["iso_code", "date", "new_cases", "new_vaccinations", "new_tests"])

COVIDdf = pd.read_csv('cleanedForCaseSentiment.csv') #just needs to read as saved processed to the file to speed up testing


def groupDFByMonth(iso_col_name, code, df):
    isCountry = df[iso_col_name]==code
    df = df[isCountry]
    dates = pd.to_datetime(df['date'])
    df['date'] = dates
    df = df.set_index('date')
    return df.groupby(pd.Grouper(freq='M')).mean()


def joinDF(iso_code):
    whoiso = groupDFByMonth("iso_code", iso_code, WHOdf)
    covidiso = groupDFByMonth("iso_code", iso_code, COVIDdf)
    whoiso.join(covidiso)
    MERGEDdf = pd.merge(whoiso, covidiso, left_index=True, right_index=True)
    MERGEDdf = MERGEDdf.reset_index()
    return MERGEDdf

def plot(WHOdf, COVIDdf, iso_code, vaccine=False, tests=False):
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
    plt.show()

def getCorrelationTable(column):
    COUNTRIES = np.unique(COVIDdf['iso_code'])
    correlationsCountry = []
    for country in COUNTRIES:
        df = joinDF(country)
        df = df[['compound', column]]
        df.dropna(0, inplace=True)
        sentiment = df['compound']
        var = df[column]
        if len(sentiment)>10:
            corr, p = pearsonr(sentiment, var)
            correlationsCountry.append({'iso_code': country, 'correlation':corr})
    correlationsCountry = pd.DataFrame(correlationsCountry)

    correlationsCountry.sort_values('correlation', inplace=True)
    print(correlationsCountry.head(30))

def changeInReaction(cases, sentiment):
    casesDiffs = []
    for i in range(len(cases)):
        percentageChange = (cases[i+1]-cases[i])/cases[i]
        casesDiffs.append(percentageChange)
    df['new_cases'].pct_change()
    #COMPARE
    #PERCENTAGE CHANGE FOR SENTIMENT
    #PLOT BOTH
    #SHOW WITH MOST NEGATIVE CORRELATION






getCorrelationTable('new_vaccinations')


# plot(WHOdf, COVIDdf, "FIN")
# plot(WHOdf, COVIDdf, "CHN")
# plot(WHOdf, COVIDdf, "IRL")
# plot(WHOdf, COVIDdf, "BEL")
# plot(WHOdf, COVIDdf, "NZL")