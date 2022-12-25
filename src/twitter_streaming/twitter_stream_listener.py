"""Implements main class for twitter tracking logic

"""

import json
import time
from datetime import datetime

import tweepy
from tweepy.streaming import StreamListener

from src.constants import DATA_TWITTER
from src.logger_definition import get_logger

logger = get_logger(__file__)


class TwitterStreamListener(StreamListener):
    """Stream listener class for twitter streaming

    Personalized tweepy StreamListener class for our streaming needs. Implements the save to output
    every minute requirement.
    """

    def __init__(self, credentials: dict):
        # Initialize authenticated api with credentials dict
        self.tweepy_oauth(credentials)
        # Register start time at initialization
        self.start_time = time.time()
        # Initialize batch of tweets to dump as empty dict
        self.tweet_batch = dict()

    def tweepy_oauth(self, twitter_credentials: dict):
        """Helper method for twitter API OAUTH

        Args:
            twitter_credentials (dict): API credentials
        """
        auth = tweepy.OAuthHandler(
            twitter_credentials["TWITTER_APP_KEY"], twitter_credentials["TWITTER_APP_SECRET"]
        )
        auth.set_access_token(
            twitter_credentials["TWITTER_KEY"], twitter_credentials["TWITTER_SECRET"]
        )

        api = tweepy.API(auth)

        if api.verify_credentials():
            logger.info("Authentication OK")
        else:
            # TODO: change value error for some sort of authentication error
            raise ValueError("Unable to authenticate to twitter API, check credentials.")

        self.api = api

    def on_status(self, tweet):
        # If a minute has passed since start time
        if (time.time() - self.start_time) / 60 >= 1:
            # Save current tweet batch
            with open(DATA_TWITTER / f"twitter_dump_{str(datetime.now())}.json", "w") as f:
                json.dump(self.tweet_batch, f)

            # Restart timer and tweet batch
            logger.info("Batch save successfull, processing next batch")
            self.start_time = time.time()
            self.tweet_batch = dict()

        # Append current tweet to batch
        self.tweet_batch.update({tweet.user.name: tweet.text})

    def on_error(self, status):
        # Disconnect on too many requests error
        if status == 420:
            return False
