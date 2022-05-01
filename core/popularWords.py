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
from nltk.sentiment.vader import SentimentIntensityAnalyzer


#Get current directory for saving images
cwd = Path.cwd()
mod_path = Path(__file__).parent


pd.options.mode.chained_assignment = None # default='warn' this is needed for false positives warnings on reassigning pd dataframe

def getPopularWords(df, amountNeeded):#Input a list of strings and amount of popular words needed, returns a list of popular words
  inOne = ""

  for messages in df.cleaned_words.tolist():
        words = messages.split(",")
        for word in words:
            inOne += word[2:-1].replace("'","") + " "
  justWords = inOne.split()#Splitting into words
  popularWords = Counter(justWords)
  return (popularWords.most_common(amountNeeded))#Looked into source code of counter and appears to be O(n) time complexity

def SentimentOfPopularWords(df,amountNeeded,wordFile):
    popularWords = getPopularWords(df,amountNeeded)
    sia = SentimentIntensityAnalyzer()
    total = 0
    toDiv = 0
    for words in popularWords:
        score = sia.polarity_scores(words[0])["compound"]*words[1]
        total += score
        toDiv += words[1]
        
        try: wordFile.write(str(words[0] + " " + str(words[1]) + " " + str(sia.polarity_scores(words[0])["pos"]) + " " + str(sia.polarity_scores(words[0])["neg"]) + " " + str(sia.polarity_scores(words[0])["compound"]) + ","))
        except: wordFile.write(str("EMOJI" + " " + str(words[1]) + " " + str(sia.polarity_scores(words[0])["pos"]) + " " + str(sia.polarity_scores(words[0])["neg"]) + " " + str(sia.polarity_scores(words[0])["compound"]) + ","))
    total = total / toDiv
    wordFile.write(str("\n" + str(total)))
    return total
    #SentimentAnalysis

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
    wc = WordCloud(background_color='black',stopwords=None,min_word_length=2,collocations=False).generate(strText)
    plt.figure()
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.savefig(path)
    #plt.show()


#Generate one WordCloud per month
COVIDdf = COVIDdf[COVIDdf["lang"]=="en"]
strText = splitByMonth(COVIDdf)
direct = 'NoBigrams/'
WordSentimentFile = open("SentimentOfPopularWords.txt","w")
WordSentimentFile.write("Per month: words separated by commas with: word count pos neg compound \n")
for month in strText:
    #fileName = direct + str(month.iloc[0]["datetime"].to_period('M')) + ".png"
    fileName = direct + str(month.iloc[0])[-34:-27] + ".png"

    src_path = (mod_path / fileName).resolve()
    #gen(dfTextToString(month), src_path)
    WordSentimentFile.write(str(month.iloc[0])[-34:-27])
    print(str(month.iloc[0])[-34:-27])
    WordSentimentFile.write("\n")
    SentimentOfPopularWords(month,200,WordSentimentFile)
WordSentimentFile.close()


#Generate Overall WordCloud
fileName = direct + "Overall.png"
src_path = (mod_path / fileName).resolve()
gen(dfTextToString(COVIDdf), src_path)
