from collections import Counter
import pandas as pd
import json
import matplotlib.pyplot as plt
from cleaner import stripFillerWords
from sentiment_analysis import create_cleaned

def getPopularWords(df, amountNeeded):#Input a list of strings and amount of popular words needed, returns a list of popular words
  inOne = ""

  for message in df.text:
    inOne += message + " "
  justWords = inOne.split()#Splitting into words
  popularWords = Counter(justWords)
  return (popularWords.most_common(amountNeeded))#Looked into source code of counter and appears to be O(n) time complexity



from wordcloud import WordCloud
with open("./processed_data/final_df.json", "r") as file:
    COVIDdf = pd.read_json(json.load(file))


def dfTextToString(df):
    df = create_cleaned(COVIDdf, 'text')
    text = df['cleaned_words'].tolist()
    text = [' '.join(s) for s in text]
    strText = ' '.join(text)
    return strText

strText = dfTextToString(COVIDdf)

wc = WordCloud(stopwords=None).generate(strText)
plt.figure()
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.show()