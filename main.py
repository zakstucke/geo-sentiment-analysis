from core.twitter_scraper import TwitterScraper



def main():
    scraper = TwitterScraper()
    
    data = scraper.get_recent_tweets("Ukraine", max_tweets_about=1000)

    print(data)


if __name__ == "__main__":
    main()
