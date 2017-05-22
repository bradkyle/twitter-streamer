import tweepy
from twit import StreamListener
from auth import current_auth
from config import WORDS

#Set up the listener. The 'wait_on_rate_limit=True' is needed to help with Twitter API rate limiting.
listener = StreamListener(api=tweepy.API(retry_count=6))
streamer = tweepy.Stream(auth=current_auth(), listener=listener)

#filter the stream utilizing the WORDSas specified
print("Tracking: " + str(WORDS))
streamer.filter(track=WORDS)