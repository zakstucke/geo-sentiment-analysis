#HYPOTHESIS: People's sentiment in tweets has become increasingly mild as a reaction to rises/falls in cases/deaths over the past two years
#Country Basis plot the days case level alongside average sentiment per day/week/month

import pandas as pd
import json
import matplotlib.pyplot as plt
import pycountry
import datetime
from scipy.stats import pearsonr

pd.options.mode.chained_assignment = None  # default='warn' this is needed for false positives warnings on reassigning pd dataframe

#CASES DATA FROM CSV
WHOfile = "data/WHO_covid_data_by_COUNTRY.csv"
WHOdf = pd.read_csv(WHOfile, usecols=["iso_code", "date", "new_cases", "total_vaccinations"])
# WHOVaccinedf = pd.read_csv(WHOfile, usecols=["iso_code", "date", "total_vaccinations"])
#TWEET DATA FROM PREPROCESSED DF
# with open("./processed_data/final_df.json", "r") as file:
#     COVIDdf = pd.read_json(json.load(file))
COVIDdf = pd.read_csv('processed_data/final_csv.txt')

COVIDdf.rename(columns={'created_at': 'date'}, inplace=True)
# justvaccines = WHOdf[WHOdf['total_vaccinations']].notna()
# print(justvaccines.head)
#lookup iso-3 country code
def normaliseCC(row):
    code = row['iso_code']
    iso3 = pycountry.countries.get(alpha_2=code)
    if iso3:
        return iso3.alpha_3
    else:
        return code

def cleanTweetDF(df):
    df = df[df["iso_code"].notna()]
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

def plot(WHOdf, COVIDdf, iso_code, vaccine=False):
    whoiso = groupDFByMonth("iso_code", iso_code, WHOdf)
    covidiso = groupDFByMonth("iso_code", iso_code, COVIDdf)

    title = iso_code + " Avg Daily New Cases By Month over Covid with Average Sentiment of Tweets Regarding COVID"
    whoiso.join(covidiso)
    df = pd.merge(whoiso, covidiso, left_index=True, right_index=True)
    df = df.reset_index()

    fig, ax = plt.subplots(figsize=(10,5))

    if vaccine:
        print('vaccines', df.total_vaccinations)
        ax.plot(df.date, df.total_vaccinations, color='red')
        ax.set_xlabel("Date")
        ax.set_ylabel("Total Vaccines", color="red")
        ax.set_title(title)

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


# COVIDdf = cleanTweetDF(COVIDdf)
# COVIDdf.to_csv('cleanedForCaseSentiment.csv') #saves new df as csv with normalised cc and removes nan dates to reduce loading time

COVIDdf = pd.read_csv('cleanedForCaseSentiment.csv')

#ENTER ANY COUNTRY CODE (SOME HAVE MORE TWEETS THAN OTHERS SO WILL SHOW BETTER RESULTS)
# plot(WHOdf, COVIDdf, "GBR")
# plot(WHOdf, COVIDdf, "RUS")
# plot(WHOdf, COVIDdf, "USA")
# plot(WHOdf, COVIDdf, "DEU")
# plot(WHOdf, COVIDdf, "CAN")

def lockdownUK():
    df = groupDFByMonth("iso_code", "GBR", COVIDdf)
    df = df.reset_index()
    title = " UK Average Sentiment of Tweets Regarding COVID with lockdown information"
    fig, ax = plt.subplots(figsize=(10,5))
    ax.plot(df.date, df.compound, color='blue')
    ax.set_xlabel("Date")
    ax.set_ylabel("Average Sentiment", color='blue')
    ax.set_title(title)
    keydates = {'First Lockdown Starts':"2020, 03, 26",
                'Pubs Reopen':"2020, 06, 04",
                "Eat Out To Help Out": "2020, 08, 03",
                "Rule of Six Introduced":"2020, 09, 14",
                "Second Lockdown Starts":"2020, 11, 05",
                "Christmas Cancelled":"2020, 12, 21",
                "Third Lockdown":"2021, 01, 06",
                "Schools Reopen":"2021, 03, 08",
                "Hospitality Reopens":"2021, 04, 12",
                "COVID Passes Needed":"2021, 12, 15",
                "Covid Rules Scrapped":"2022, 02, 24"
                }
    dates = [datetime.datetime.strptime(date, '%Y, %m, %d') for title, date in keydates.items()]

    for date in dates:
        plt.axvline(x=date)
    ax.legend(keydates.keys())
    plt.show()

lockdownUK()


