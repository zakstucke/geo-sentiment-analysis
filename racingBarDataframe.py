from collections import Counter
import pandas as pd
from core.sentiment_analysis import create_cleaned
import spacy
from spacy_langdetect import LanguageDetector

nlp = spacy.load("en_core_web_sm")
nlp.add_pipe(LanguageDetector(), name="language_detector", last=True)
stop_words = nlp.Defaults.stop_words


pd.options.mode.chained_assignment = None  # default='warn' this is needed for false positives warnings on reassigning pd dataframe


def getPopularWords(df, amountNeeded):#Input a list of strings and amount of popular words needed, returns a list of popular words
  inOne = ""
  for message in df.text:
    doc = nlp(message)
    if doc._.language['language'] == 'en':
        inOne += message + " "
  justWords = inOne.split()#Splitting into words
  popularWords = Counter(justWords)
  return (popularWords.most_common(amountNeeded))#Looked into source code of counter and appears to be O(n) time complexity

def dfTextToString(df):
    df = create_cleaned(df, 'text')
    text = df['cleaned_words'].tolist()
    text = [' '.join(s) for s in text]
    strText = ' '.join(text)
    return strText

def splitByMonth(df):
    df = df[df["created_at"].notna()]
    dates = pd.to_datetime(df['created_at'])
    df['created_at'] = dates
    df = df.set_index('created_at')
    strText = []
    for group_name, df_group in df.groupby(pd.Grouper(freq='M')):
        strText.append(df_group)
    return strText

def groupDFByMonth(df):
    df = df[df["created_at"].notna()]
    dates = pd.to_datetime(df['created_at'])
    df['created_at'] = dates
    df = df.set_index('created_at')
    return df.groupby(pd.Grouper(freq='M'))



COVIDdf = pd.read_csv('processed_data/final_csv.txt')
grouped = groupDFByMonth(COVIDdf)


table = []
for month,df in grouped:
    df = create_cleaned(df, 'text')
    popWords = getPopularWords(df, 30)
    row = {'month':month}
    for (word, count) in popWords:
        row.update({word:count})
    table.append(row)

Outdf = pd.DataFrame(table)
Outdf.set_index('month')
Outdf.to_csv('test.csv')

df = pd.read_csv('test.csv')
df = df.transpose()
print(df)
df.to_csv('racingDF.csv')