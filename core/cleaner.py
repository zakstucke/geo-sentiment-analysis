import spacy

nlp = spacy.load("en_core_web_sm")


def getSingleTweet(data):  # Used for original Main data scraped by TwitterScraper
    # Dictionary has 2 keys
    #       data - for tweet data
    #       includes - for user data
    # Data is made up of a list of tweets, each tweet is its own dictionary
    # This dictionary consists of:
    #                           -id
    #                           -referencedtweets (A list containing a dict for each referenced tweet
    #                           -public_metrics (A dict with: retweet_count,reply_count,like_count,quote_count
    #                           -possibly_sensitive: Bool
    #                           -created_at
    #                           -text
    #                           -lang
    tweetList = data["data"]
    singleTweet = tweetList[0]
    return singleTweet


def getText(data):  # Used for original Main data scraped by TwitterScraper
    tweetList = data["data"]
    allText = []
    counter = 0
    for tweet in tweetList:
        allText.append(str(counter) + ": " + tweet["text"] + "\n\n")
        counter += 1
    return allText


def stripFillerWords(
    words,
):  # Takes a list of words as input and returns list with filler/stop words removed

    # Remove normal filler words (so, was etc):
    result = [word for word in words if word not in nlp.Defaults.stop_words]

    return result
