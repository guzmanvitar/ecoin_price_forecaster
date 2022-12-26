"""Runs the twitter tracking job. Run

    src/twitter_streaming/twitter_tracker.py --help

for usage help.
"""

import argparse

import tweepy

from src.constants import TWITTER_CREDENTIALS
from src.twitter_streaming.twitter_stream_listener import TwitterStreamListener

if __name__ == "__main__":
    parser = argparse.ArgumentParser("twitter_tracker")

    parser.add_argument(
        "-t",
        "--track",
        nargs="+",
        default=["christmas"],
        help="Terms to track on twitter",
    )

    args = parser.parse_args()

    tweets_listener = TwitterStreamListener(TWITTER_CREDENTIALS)
    stream = tweepy.Stream(tweets_listener.api.auth, tweets_listener)
    stream.filter(track=args.track, languages=["en"])
