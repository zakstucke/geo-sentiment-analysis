import pandas as pd
import json
import matplotlib.pyplot as plt
import pycountry
import datetime
from scipy.stats import pearsonr
import numpy as np

pd.options.mode.chained_assignment = None  # default='warn' this is needed for false positives warnings on reassigning pd dataframe

# WHOfile = "data/WHO_covid_data_by_COUNTRY.csv"
# WHOdf = pd.read_csv(WHOfile, usecols=["iso_code", "date", "new_cases", "new_vaccinations", "new_tests"])

# #COVIDdf = pd.read_csv('cleanedForCaseSentiment.csv') #just needs to read as saved processed to the file to speed up testing

# COVIDdf = pd.read_csv('processed_data/final_csv.txt')
# COVIDdf.rename(columns={'created_at': 'date'}, inplace=True)


dictionary = {'AK': (0.41907715530782635, -0.24537150333353125, False), 'AL': (0.4315520381744366, -0.21963934838989863, False), 'AR': (0.13407237538852396, 0.4051755925832934, False), 'AZ': (0.3212129960180458, 0.2749990046380907, False), 'CA': (0.6855092544793175, 0.11411679678375226, False), 'CO': (0.6833996163461826, 0.11492064277013786, False), 'CT': (0.5433341170582301, -0.17770218018133316, False), 'DE': (0.4792840875630574, -0.2062568089495694, False), 'FL': (0.18831065942801714, 0.35937872123108605, False), 'GA': (0.8003174166209478, 0.07142076135664802, False), 'HI': (0.7562957447954272, -0.08757518704265445, False), 'IA': (0.47182924861309433, 0.20132588032947757, False), 'ID': (0.9732421246806225, 0.009483204741854878, False), 'IL': (0.9709297051593461, 0.010303051070367455, False), 'IN': (0.500298389329485, 0.1888375218959172, False), 'KS': (0.397512765260647, -0.2358065847768691, False), 'KY': (0.2544276875974118, 0.31397971329007707, False), 'LA': (0.11679369277977635, 0.42237181070645125, False), 'MA': (0.2960879530011792, 0.2890436517992506, False), 'MD': (0.644346181122446, 0.12995936142950362, False), 'ME': (0.09386789628421847, 0.6783966311196863, False), 'MI': (0.12132588901961158, 0.4177010819208654, False), 'MN': (0.1484085287943251, 0.39201978748331956, False), 'MO': (0.3564551173729067, -0.2563206322097375, False), 'MS': (0.7743182578062676, -0.08093359291951864, False), 'MT': (0.9079078424730914, 0.0340855240442699, False), 'NC': (0.26404247322043256, 0.30801829457120455, False), 'ND': (0.5908149383172604, -0.1574745952847917, False), 'NE': (0.01075410820374891, 0.6363684522839479, True), 'NH': (0.1927194923276158, 0.6161643510994979, False), 'NJ': (0.09656103245821505, -0.44491019176575564, False), 'NM': (0.5441437400688679, -0.17023101878185642, False), 'NV': (0.014757297453465035, 0.614654270738406, True), 'NY': (0.8874601461610407, -0.03999548859326904, False), 'OH': (0.9783820328642071, -0.0076611414900575325, False), 'OK': (0.8724074615467825, -0.045383251867331505, False), 'OR': (0.8904055505250477, -0.03894279745074948, False), 'PA': (0.7077821261394852, 0.10567868849719592, False), 'RI': (0.2496628670426442, 0.316985065020106, False), 'SC': (0.6548694581595924, 0.12587622427167605, False), 'SD': (0.5941287087067796, 0.14979983565978972, False), 'TN': (0.7458634602083715, -0.09143910296752672, False), 'TX': (0.21811986844477982, 0.33783836907188647, False), 'UT': (0.9341766107063042, -0.023347805488491746, False), 'VA': (0.3134699331092026, 0.4991383319331629, False), 'VT': (0.6179624692372041, 0.5647276037761855, False), 'WA': (0.5144893553777465, 0.1827371902114813, False), 'WI': (0.39372265439925486, -0.23765092342379612, False), 'WV': (1.0, -1.0, False), 'WY': (0.7134379828466156, 0.14308452894003304, False)}
df = pd.DataFrame(dictionary)
df.to_csv('stateCorrelation.csv')

def hypothesisTest(x, y, alpha):
    likelyDependent = False
    x = x[~np.isnan(x)]
    if len(x)<len(y):
        y = y[-len(x):]
    print(x,y)
    corr, p = pearsonr(x, y)
    if p < alpha:
        likelyDependent = True
    return p, corr, likelyDependent



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
    #correlationsCountry.sort_values('correlation', inplace=True)
    

def changeInReaction(column, country):
    df = joinDF(country)
    df = df[['compound', column]]
    df.dropna(0, inplace=True)
    df['compoundChange'] = df['compound'].pct_change()
    df['casesChange'] = df[column].pct_change()
    df['effect'] = (df['compoundChange']/df['casesChange']).abs()
    diff = np.array(df['effect'])[1::]
    x=np.linspace(1,len(diff),len(diff))
    if x.any() and diff.any():
        m, b = np.polyfit(x, diff, 1)
        if m:
            return {'country': country, 'gradient':m}
    else:
        return {'country': country, 'gradient':0}

def changeInReactionPLOT(column, country):
    df = joinDF(country)
    df = df[['compound', column]]
    df.dropna(0, inplace=True)
    df['compoundChange'] = df['compound'].pct_change()
    df['casesChange'] = df[column].pct_change()
    df['effect'] = (df['compoundChange']/df['casesChange']).abs()
    diff = np.array(df['effect'])[1::]
    x=np.linspace(1,len(diff),len(diff))
    m, b = np.polyfit(x, diff, 1)
    plt.plot(x, m*x+b)
    plt.plot(x, diff, 'o')
    plt.title(str(country)+" Percentage Change In Sentiment Relative to Percentage Change in Cases")
    plt.ylabel("\% Change")
    plt.xlabel('Months')
    plt.show()

def vaxTweetFilter(df):
    vaxDF =df[df['text'].str.contains("vax", False)]
    vaccDF = df[df['text'].str.contains("vacc", False)]
    df = pd.concat([vaxDF, vaccDF]).drop_duplicates().reset_index(drop=True)
    df = df[df['lang']=='en']
    return df


def stateBarChart(df):
    df = df.transpose()
    print(df)
    df = df.rename(columns={0: "p", 1: "corr", 2: "likelyDependent"})
    print(df)
    return df

stateDF = pd.read_csv('stateCorrelation.csv')
stateBarChart(stateDF)

#vaxTweetFilter(COVIDdf)

# casesCorr = getCorrelationTable('new_cases')
# vaxCorr = getCorrelationTable('new_vaccinations')
# vaxCorr.sort_values('correlation', ascending=False, inplace=True)
# casesCorr.sort_values('correlation', inplace=True)

# print(casesCorr.head(10))
# print(vaxCorr.head(10))

# vaxCol = vaxCorr['correlation']
# print(len(vaxCol))
# print('Positive Vax Corr', vaxCol[vaxCol>=0].count())
# print('Strong Positive Vax corr  > 0.25', vaxCol[vaxCol>=0.25].count())


# corrCol = casesCorr['correlation']
# print(len(corrCol))
# print(corrCol[corrCol>=0].count())
# print('NEgative corr <= -0.5', corrCol[corrCol<=-0.25].count())

# COUNTRIES = np.unique(COVIDdf['iso_code'])
# gradients = []
# for country in COUNTRIES:
#     gradients.append(changeInReaction('new_cases', country))
# gradientsDF = pd.DataFrame(gradients)
# gradientsDF.sort_values('gradient', ascending=True, inplace=True)
# print(gradientsDF.head(20))

# gradientsCol = gradientsDF['gradient']
# print('Negative gradient on percetnage change', gradientsCol[gradientsCol<0].count())
# print("Percentage change for ", len(gradientsDF))

# COUNTRIES = np.unique(COVIDdf['iso_code'])
# vgradients = []
# for country in COUNTRIES:
#     vgradients.append(changeInReaction('new_vaccinations', country))
# vgradientsDF = pd.DataFrame(vgradients)
# vgradientsDF.sort_values('gradient', ascending=True, inplace=True)
# print(vgradientsDF.head(20))

# vgradientsCol = vgradientsDF['gradient']
# print('Negative gradient on percetnage change',vgradientsCol[vgradientsCol<0].count())
# print("Percentage change for ", len(vgradientsDF))
# # changeInReaction('new_cases', 'ZAF')
# plot(WHOdf, COVIDdf, 'TUR', "new_vaccinations")
# plot(WHOdf, COVIDdf, 'THA', "new_vaccinations")
# plot(WHOdf, COVIDdf, 'IRL', "new_vaccinations")
# plot(WHOdf, COVIDdf, 'USA', "new_vaccinations")
# plot(WHOdf, COVIDdf, 'DEU', "new_vaccinations")
# # plot(WHOdf, COVIDdf, "CHN")
# # plot(WHOdf, COVIDdf, "IRL")
# # plot(WHOdf, COVIDdf, "BEL")
# # plot(WHOdf, COVIDdf, "NZL")

# df = joinDF('GBR')
# df = df[['compound', 'new_cases']]
# df.dropna(0, inplace=True)
# df['compoundChange'] = df['compound'].pct_change()
# df['casesChange'] = df["new_cases"].pct_change()
# df['effect'] = (df['compoundChange']/df['casesChange']).abs()
# diff = np.array(df['effect'])[1::]
# print(df)

# print(df['compoundChange'])