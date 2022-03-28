#IMPORT DEATHS AND CASES FROM WHO DATASET
#FETCH TWEETS 
#HYPOTHESIS: People's sentiment in tweets has become increasingly mild as a reaction to rises/falls in cases/deaths over the past two years
#Country Basis plot the days case level alongside average sentiment per day/week/month


#GET NEW_CASES COL FROM WHO CSV

#FROM TWEET SELECTION IN A COUNTRY GET AVERAGE SENTIMENT VALUES

#PLOTTER()

from main import read_final_df
import pandas as pd
import json
import matplotlib.pyplot as plt
#parse_raw_csv("/data/WHO_covid_data_by_country.csv", "processed_data/WHO_country_df.json")

WHOfile = "data/WHO_covid_data_by_COUNTRY.csv"
#data/WHO_covid_data_by_COUNTRY.csv

WHOdf = pd.read_csv(WHOfile, usecols=["iso_code", "date", "new_cases"])

#print(WHOdf.head())

#CLEAN DATA AS LOTS OF NANs


#covid sentiment scores by country with dates
with open("./processed_data/final_df.json", "r") as file:
    COVIDdf = pd.read_json(json.load(file))

#COVIDdf = read_final_df("./processed_data/final_df.json")

#print(COVIDdf.head())
#cols in COVID df = data, 

#print(COVIDdf)

#matplot

# def tweetSentimentOverTime(ISO_code tweetDF, timeRange):
#     tweetDF = tweetDF.filter(ISO_code)
#     return tweetDF.groupby(pd.Grouper(freq='M')).mean()
#     monthSentiment = {}
#     for month in timeRange:
#         sentimentForMonth = tweetDF.at(month)
#         totalSentiment = sum(sentimentForMonth)
#         avgSentiment = totalSentiment/len(sentimentForMonth)
#         monthSentiment.update({month: avgSentiment})
#     return monthSentiment

def groupDFByMonth(iso_col_name, code, df):
    #input df formatted by date for one country with either sentiment val or daily new cases
    isCountry = df[iso_col_name]==code
    df = df[isCountry]
    dates = pd.to_datetime(df['date'])
    df['date'] = dates
    df = df.set_index('date')
    return df.groupby(pd.Grouper(freq='M')).mean()


def createMonthCaseSentimentDF(whoDF, covidDF, ISO):
    whoMeans = groupDFByMonth("iso_code", ISO, whoDF)
    dates = whoMeans['date']
    cases = whoMeans['new_cases']
    #need to sort country codes to iso codes in tweet df
    covidMeans = groupDFByMonth("country_code", ISO, covidDF)
    coviddates = covidMeans['created_at']
    covidsentiments = covidMeans['sentiment']
    #join on months somehow


def plot(WHOdf, iso_code):
    #start = isoWHOdf[0]['date']
    #end = isoWHOdf[-1]['date']
    #timeRange = pd.date_range(start, end, freq='M')
    newDF = groupDFByMonth("iso_code", iso_code, WHOdf)
    title = iso_code + " Avg Daily New Cases By Month over Covid"
    newDF.plot(xlabel="Months", ylabel="Avg Daily Cases", title=iso_code)
    plt.show()
    #y = newDF['new_cases']
    #print(y)
    #plt.plot(x, y)
    #plt.show()
    

#print(groupDFByMonth("iso_code", "GBR", WHOdf))
plot(WHOdf, "GBR")   


