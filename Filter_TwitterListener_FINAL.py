import tweepy
import requests
from textblob import TextBlob
import dataset
from platform import python_version
from better_profanity import profanity
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# note: the imports platform and requests are to support the initializer
# this class overrides many of the methods in the tweepy library in order
# to get my desired behavior, it's probably a good idea to look at the tweepy
# source code if you plan to make significant customizations


class Filter(tweepy.Stream):

    def __init__(self, consumerKey, consumerSecret, accessToken,
                 accessTokenSecret, tweet_count, keyword):
        self.process_count = 0
        self.consumer_key = consumerKey
        self.consumer_secret = consumerSecret
        self.access_token = accessToken
        self.access_token_secret = accessTokenSecret
        self.limit = tweet_count
        self.chunk_size = 512
        self.daemon = False
        self.max_retries = 100
        self.verify = True
        self.proxies = {"https": None} if None else {}
        self.running = False
        self.session = None
        self.thread = None
        self.keywords = keyword
        self.print_count = 0
        self.user_agent = (
            f"Python/{python_version()} "
            f"Requests/{requests.__version__} "
            f"Tweepy/{tweepy.__version__}")

    def on_status(self, status: object):

        # Logic to close the connection after a certain number of tweets
        # are retrieved otherwise the connection will stay open indefinitely
        # or until there is an issue that cause it to close since it's not
        # a guaranteed pipe

        if self.process_count == self.limit:
            # exit app
            self.disconnect(1)

        # removing retweets to help avoid duplicates
        if status.retweeted or 'RT @' in status.text:
            return

        # to do: add feature to remove tweets with
        # sensitive content, e.g. videos or photos

        # acquiring location, converting coordinates to string
        # as it's easier to handle
        location = status.coordinates
        if location:
            location = str(status.coordinates['coordinates'])

        # ensure we grab exteded tweets when available
        if hasattr(status, "extended_tweet"):
            tweet_text = status.extended_tweet['full_text']
        else:
            tweet_text = status.text

        # inserts a field that will let us know what keyword
        # was used to filter an individual tweet
        keyword = self.check_keyword(tweet_text)
        if not keyword:
            return

        # Commented out, but the feature to reject tweets
        # containing profanity is here if desired
        # if profanity.contains_profanity(tweet_text):
        # return

        # text blob analysis - text blob generates two types of scores
        # Polarity a score between -1 and 1, where -1 is negative
        # sentiment and +1 is positive, subjectivity, which lies beteen 0 and 1
        blob = TextBlob(tweet_text)
        tweet_sentiment = blob.sentiment
        polarity = tweet_sentiment.polarity
        subjectivity = tweet_sentiment.subjectivity

        # Vader sentiment analysis, which returns three probabilities for
        # a given sentence being positive, negative or neutral, with all
        # the probabilities adding up to 1. E.g., a sentence scores 0.24
        # for negative, 0.7 for positive and 0.06 for neutral a compound
        # score is also generated that is the overall score the sentence
        # Vader is optimized for social media, so it "should" give better
        # sentiment scores for Twitter

        # generate each of the sentiment scores
        # score is a dictionary with the following keys:
        score = SentimentIntensityAnalyzer().polarity_scores(tweet_text)

        positive = score['pos']
        negative = score['neg']
        neutral = score['neu']
        compound = score['compound']

        # for more accurate analytics but displaying tweets in public
        # censors profanity in the original tweet, but only after sentiment
        # has been calculated comment out when using the earlier code to
        # reject all tweets with profanity
        tweet_text = profanity.censor(tweet_text)

        # if you don't have the DB or table created, it will be created
        # for you automatically
        # insert your own names for the db and the table 
        db = dataset.connect("sqlite:///filtertweetsdb.db")

        table = db['filter_tweet_table']
        table.insert(dict(
            keyword=keyword,
            text=tweet_text,
            timeStamp=status.created_at,
            verified_user=status.user.verified,
            followers=status.user.followers_count,
            retweetCount=status.retweet_count,
            favoriteCount=status.favorite_count,
            location=location,
            textblob_sentiment=polarity,
            textblob_subjectivity=subjectivity,
            vader_compound=compound,
            vader_positive=positive,
            vader_negative=negative,
            vader_neutral=neutral,))

        # print tweet just to observe things working
        # print(tweet_text)

        # increment the tweet counter and the counter for printing
        # every nth tweet
        self.process_count += 1
        self.print_count += 1

        # printing every 10th tweet
        if self.print_count == 10:
            print(tweet_text)  # printing every 10th tweet
            self.print_count = 0  # reseting counter

    # manage errors and hitting the limit on retrieving tweets
    # limits wouldn't occur as the endpoint this class connects to
    # doesn't have a limit. However, there are limits as to the
    # number of attempts to reconnect in case of a connection error
    def on_error(self, status_code: int):

        if status_code == 420:
            # print error message
            print("reached max limit and/or connection timed out")

            # exit app
            self.disconnect(self.tweet_df, 0)

    # ensures a more elegant disconnect sequence the flag is meant
    # to show a custom message instead of the "Twitter Disconnected"
    # message needed to override the "on_disconnect()" to make that
    # happen.

    def disconnect(self, flag: int):

        if flag == 1:
            print('stream disconnecting, desired sample size received')
        else:
            print('connection issue present, stream disconnecting')

        self.running = False

    # ensures that each record has a field that indicates the specific
    # phrase that was used to filter it out of the stream
    def check_keyword(self, body: object):
        for keyword in self.keywords:
            if keyword in body:
                return keyword
        return None
