from collections import Counter
def getPopularWords(df, text_column_name, amountNeeded):#Input a list of strings and amount of popular words needed, returns a list of popular words
  inOne = ""

  for message in df.text:
    inOne += message + " "
  justWords = inOne.split()#Splitting into words
  popularWords = Counter(justWords)
  return (popularWords.most_common(amountNeeded))#Looked into source code of counter and appears to be O(n) time complexity

