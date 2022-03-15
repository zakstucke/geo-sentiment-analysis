from core.twitter_scraper import TwitterScraper
import cleaner
import scraper
import pandas as pd
def cleanerTest():
    df = pd.read_csv("covidvaccine.csv", usecols= ["text"])
    print(df)
    betterDF = []
    counter = 0
    for x in df["text"].values:
        if counter == 100:
            break
        betterDF.append(x)
        counter += 1
    df = betterDF
    splitWords = cleaner.splitToWords(df)
    print("###############WORDS")
    print(splitWords)
    stripPunctuation = cleaner.stripPunctuation(splitWords)
    print("###############PUNCTUATION")
    print(stripPunctuation)
    stripFillerWords = cleaner.stripFillerWords(stripPunctuation)
    print("###############FILLER")
    print(stripFillerWords)

def main():
    #tweetScraper = TwitterScraper()
    
    #data = tweetScraper.get_recent_tweets("Ukraine", max_tweets_about=10)
    #singleTweet = cleaner.getSingleTweet(data)
    #print(singleTweet)
    #tweetTextList = cleaner.getText(data)
    #for tweet in tweetTextList:
    #    print(tweet)
    cleanerTest()
if __name__ == "__main__":
    main()
