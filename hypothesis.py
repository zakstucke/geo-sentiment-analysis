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

def plot(WHOdf, COVIDdf, iso_code, col):
    whoiso = groupDFByMonth("iso_code", iso_code, WHOdf)
    covidiso = groupDFByMonth("iso_code", iso_code, COVIDdf)
    title = iso_code + " Avg Daily New Vaccinations By Month over Covid with Average Sentiment of Tweets Regarding COVID"
    whoiso.join(covidiso)
    df = pd.merge(whoiso, covidiso, left_index=True, right_index=True)
    df = df.reset_index()
    fig, ax = plt.subplots(figsize=(10,5))
    ax.plot(df.date, df[col], color='red')
    ax.set_xlabel("Date")
    ax.set_ylabel("New Vaccinations", color="red")
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
    return correlationsCountry
    correlationsCountry.sort_values('correlation', inplace=True)
    

def changeInReaction(column, country):
    df = joinDF(country)
    df = df[['compound', column]]
    df.dropna(0, inplace=True)

    df['compoundChange'] = df['compound'].pct_change()
    df['casesChange'] = df[column].pct_change()
    df['effect'] = (df['compoundChange']/df['casesChange']).abs()
    diff = np.array(df['effect'])[1::]
    x=np.linspace(1,len(diff),len(diff))
    # plt.plot(x, diff, 'o')
    if x.any() and diff.any():
        m, b = np.polyfit(x, diff, 1)
        if m:
            return {'country': country, 'gradient':m}
    else:
        return {'country': country, 'gradient':0}
    # plt.plot(x, m*x+b)
    # plt.title(country)
    # plt.show()


casesCorr = getCorrelationTable('new_cases')
vaxCorr = getCorrelationTable('new_vaccinations')
vaxCorr.sort_values('correlation', ascending=False, inplace=True)
casesCorr.sort_values('correlation', inplace=True)

print(casesCorr.head(10))
print(vaxCorr.head(10))

vaxCol = vaxCorr['correlation']
print(len(vaxCol))
print('Positive Vax Corr', vaxCol[vaxCol>=0].count())
print('Strong Positive Vax corr  > 0.25', vaxCol[vaxCol>=0.25].count())


corrCol = casesCorr['correlation']
print(len(corrCol))
print(corrCol[corrCol>=0].count())
print('NEgative corr <= -0.5', corrCol[corrCol<=-0.25].count())

COUNTRIES = np.unique(COVIDdf['iso_code'])
gradients = []
for country in COUNTRIES:
    gradients.append(changeInReaction('new_cases', country))
gradientsDF = pd.DataFrame(gradients)
gradientsDF.sort_values('gradient', ascending=True, inplace=True)
print(gradientsDF.head(20))

gradientsCol = gradientsDF['gradient']
print('Negative gradient on percetnage change', gradientsCol[gradientsCol<0].count())
print("Percentage change for ", len(gradientsDF))

COUNTRIES = np.unique(COVIDdf['iso_code'])
vgradients = []
for country in COUNTRIES:
    vgradients.append(changeInReaction('new_vaccinations', country))
vgradientsDF = pd.DataFrame(vgradients)
vgradientsDF.sort_values('gradient', ascending=True, inplace=True)
print(vgradientsDF.head(20))

vgradientsCol = vgradientsDF['gradient']
print('Negative gradient on percetnage change',vgradientsCol[vgradientsCol<0].count())
print("Percentage change for ", len(vgradientsDF))
# changeInReaction('new_cases', 'ZAF')
plot(WHOdf, COVIDdf, 'TUR', "new_vaccinations")
plot(WHOdf, COVIDdf, 'THA', "new_vaccinations")
plot(WHOdf, COVIDdf, 'IRL', "new_vaccinations")
plot(WHOdf, COVIDdf, 'USA', "new_vaccinations")
plot(WHOdf, COVIDdf, 'DEU', "new_vaccinations")
# plot(WHOdf, COVIDdf, "CHN")
# plot(WHOdf, COVIDdf, "IRL")
# plot(WHOdf, COVIDdf, "BEL")
# plot(WHOdf, COVIDdf, "NZL")