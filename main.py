from core.twitter_scraper import TwitterScraper
import cleaner


def main():
    scraper = TwitterScraper()
    
    data = scraper.get_recent_tweets("Ukraine", max_tweets_about=10)
    #print(data["data"][0])
    singleTweet = cleaner.getSingleTweet(data)
    print(singleTweet)
    tweetTextList = cleaner.getText(data)
    for tweet in tweetTextList:
        print(tweet)
if __name__ == "__main__":
    main()
