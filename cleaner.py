from core.twitter_scraper import TwitterScraper
import re
import spacy

def getSingleTweet(data):###Used for original Main data scraped by TwitterScraper
  #Dictionary has 2 keys
  #       data - for tweet data
  #       includes - for user data
  #Data is made up of a list of tweets, each tweet is its own dictionary
  #This dictionary consists of:
  #                           -id
  #                           -referencedtweets (A list containing a dict for each referenced tweet
  #                           -public_metrics (A dict with: retweet_count,reply_count,like_count,quote_count
  #                           -possibly_sensitive: Bool
  #                           -created_at
  #                           -text
  #                           -lang
  tweetList = data["data"]
  singleTweet = tweetList[0]
  return(singleTweet)

def getText(data):###Used for original Main data scraped by TwitterScraper
  tweetList = data["data"]
  allText = []
  counter = 0
  for tweet in tweetList:
    allText.append(str(counter) + ": " + tweet["text"] + "\n\n")
    counter += 1
  return(allText)

def splitToWords(textList): #Input list of lines, returns list of lists of words
  splitWords = []
  for line in textList:
    splitTweet = []
    print("LINE: " + line)
    words = line.split()
    for word in words:
      splitTweet.append(word)
    splitWords.append(splitTweet)
  return(splitWords)

def stripPunctuation(textList):#Input a list of words, punctuation will be removed
  strippedText = []
  for tweet in textList:
    strippedText.append([re.sub(r'[^A-Za-z0-9]+', '', x) for x in tweet])
  strippedTextNoSpace = []
  for tweet in strippedText:
    strippedTweet = []
    for word in tweet:
      if word != " ":
        strippedTweet.append(word)
    strippedTextNoSpace.append(strippedTweet)
  return(strippedTextNoSpace)

def stripFillerWords(text):#Takes a list of words as input and returns list with filler/stop words removed
  nlp = spacy.load('en_core_web_sm')
  noFillText = []
  for tweet in text:
    noFillTweet = []
    for word in tweet:
      if word not in nlp.Defaults.stop_words:
        noFillTweet.append(word)
    noFillText.append(noFillTweet)
  return(noFillText)
