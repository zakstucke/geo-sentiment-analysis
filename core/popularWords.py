from collections import Counter
import black
import pandas as pd
import json
import matplotlib.pyplot as plt
from pyparsing import Word
from cleaner import stripFillerWords
from sentiment_analysis import create_cleaned
from wordcloud import WordCloud
from wordcloud import ImageColorGenerator
from PIL import Image
import numpy as np
from pathlib import Path

#Get current directory for saving images
cwd = Path.cwd()
mod_path = Path(__file__).parent


pd.options.mode.chained_assignment = None # default='warn' this is needed for false positives warnings on reassigning pd dataframe

def getPopularWords(df, amountNeeded):#Input a list of strings and amount of popular words needed, returns a list of popular words
  inOne = ""
  for message in df.text:
    inOne += message + " "
  justWords = inOne.split()#Splitting into words
  popularWords = Counter(justWords)
  return (popularWords.most_common(amountNeeded))#Looked into source code of counter and appears to be O(n) time complexity

#with open("./processed_data/final_csv.txt", "r") as file:
COVIDdf = pd.read_csv("./processed_data/final_csv.txt")
COVIDdf.rename(columns={'created_at': 'date'}, inplace=True)

def dfTextToString(df):
    df = create_cleaned(df, 'text')
    text = df['cleaned_words'].tolist()
    text = [' '.join(s) for s in text]
    strText = ' '.join(text)
    return strText

def splitByMonth(df):
    df = df[df["date"].notna()]
    dates = pd.to_datetime(df['date'])
    df['date'] = dates
    df = df.set_index('date')
    strText = []
    for group_name, df_group in df.groupby(pd.Grouper(freq='M')):
        strText.append(df_group)
    return strText


covidImage = np.array(Image.open("./images/covidMask.jpg"))

#generate wordclouds
def gen(strText,path):
    strText = strText.replace("amp","")
    wc = WordCloud(background_color='white',stopwords=None,min_word_length=2,mask=covidImage,collocations=False).generate(strText)
    plt.figure()
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.savefig(path)
    #plt.show()


#Generate one WordCloud per month
COVIDdf = COVIDdf[COVIDdf["lang"]=="en"]
strText = splitByMonth(COVIDdf)
direct = 'NoBigrams/'
for month in strText:
    #fileName = direct + str(month.iloc[0]["datetime"].to_period('M')) + ".png"
    fileName = direct + str(month.iloc[0])[-34:-27] + ".png"

    src_path = (mod_path / fileName).resolve()
    gen(dfTextToString(month), src_path)
    


#Generate Overall WordCloud
fileName = direct + "Overall.png"
src_path = (mod_path / fileName).resolve()
gen(dfTextToString(COVIDdf), src_path)
