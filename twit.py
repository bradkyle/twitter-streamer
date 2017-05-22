from __future__ import print_function
import tweepy
import logging
import json
from db import insert_tweet, check_db
from errors import handle_error
from auth import current_auth

from config import WORDS

class StreamListener(tweepy.StreamListener):

 def on_connect(self):
     # Called initially to connect to the Streaming API
     print("You are now connected to the streaming API.")
     check_db()

 def on_error(self, status_code):
     handle_error(status_code)
     return True

 def on_timeout(self):
     print("timeout has ocurred")
     return True

 def on_disconnect(self, notice):
     handle_error(notice)


 def on_data(self, data):
     insert_tweet(data)

