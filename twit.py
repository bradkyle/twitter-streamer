from __future__ import print_function
import tweepy
import logging
import json
from pymongo import MongoClient, errors

#words to filter out of the stream
WORDS = ['bitcoin']

#Twitter access credentials
CONSUMER_KEY = "WM1MVD31TRGZBiNbXO54p4Sni"
CONSUMER_SECRET = "SJzN8rhCSyyzxt55shwpPScX1aEdOWX63q8d8yKC9gNAESsCjO"
ACCESS_TOKEN = "367687040-UzRMSNmwLjgjDl3CwAS72UbyeSkDOmKTKzmWSK89"
ACCESS_TOKEN_SECRET = "TAAu1ScD4pscR8nHTp3UyXx2T6JyCqOy5vTmcIYMtuGga"

KEY_PAIRS = [
    ["WM1MVD31TRGZBiNbXO54p4Sni", "SJzN8rhCSyyzxt55shwpPScX1aEdOWX63q8d8yKC9gNAESsCjO", "367687040-UzRMSNmwLjgjDl3CwAS72UbyeSkDOmKTKzmWSK89", "TAAu1ScD4pscR8nHTp3UyXx2T6JyCqOy5vTmcIYMtuGga"],
    ["Zv9zY9KWONeU3qKbShxq9Oat9", "Uotuon99K26RCxtUkgB7KIBMjIKLaEQ8CFoCikCkqmDAstJCBX", "860540303421448193-IgRs21k3HerMXA7eU97S90BZ3C460kF", "ab1WSco1X6jzmhNRNAnD1ieF7wmYGAKwK3ZbixwgyjuON"],
]

# CURRENT_AUTH counts the number of auth sets have been changed out due to a rate limit
CURRENT_AUTH = 0

MOCK_COUNT = 0

IS_MOCK = False

IS_DROP = False
DB_RUNNING = True

MONGO_HOST= "mongodb://mongo:27017"
client = MongoClient(MONGO_HOST)

DATABASE_NAME = "twitter"
COLLECTION_NAME = "bitcoin"

logdir = "./log/"
logging.basicConfig(filename=logdir+'info.log',level=logging.INFO)

# test_log_string = "Test"
# logging.debug(test_log_string)
# logging.info(test_log_string)
# logging.warning(test_log_string)
# logging.error(test_log_string)
# logging.critical(test_log_string)


print("----------------------------------------------- TWITTER STREAMER -----------------------------------------------")

class StreamListener(tweepy.StreamListener):
 # This is a class provided by tweepy to access the Twitter Streaming API.

 def on_connect(self):
     # Called initially to connect to the Streaming API
     print("You are now connected to the streaming API.")
     check_db()

 def on_error(self, status_code):
     handle_error(status_code)

 def on_timeout(self):
     print("timeout has ocurred")

 def on_disconnect(self, notice):
     handle_error(notice)

 def on_data(self, data):
     insert_tweet(data)

def handle_error(status_code):
    if status_code in [420, 429, 503]:
        print('Twitter streaming: temporary error occured : ' + repr(status_code))
        switch_auth()
    elif status_code in [400, 401, 403, 404, 406, 410, 422, 500, 502, 504]:
        print("Twitter streaming: leaving after an irremediable error: " + status_code)
        try:
            print("Attempting to recover by switching authentication")
            switch_auth()
        except Exception as e:
            print("Could not recover from error "+str(status_code)+" :",e)

    elif status_code in [200, 304]:
        print("Twitter streaming: " + status_code)
        return True
    else:
        print("Received unknown status: " + status_code)
        return False

def set_auths(oauth_keys):
    # initialize an empty array of authentication sets
    auths = []
    # for each of the access tokens provided in the array of access detail sets in the config.py file
    # run oauth handler and set the access token before appending to auths[]
    for consumer_key, consumer_secret, access_key, access_secret in oauth_keys:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        auths.append(auth)
    #return an array of auth sets to be used
    return auths

def switch_auth():

    print("Attempting to switch authentication.")

    # Increment a global integer variable CURRENT_AUTH
    # used to track/index the current authentication
    global CURRENT_AUTH
    CURRENT_AUTH += 1
    if CURRENT_AUTH >= len(KEY_PAIRS) :
        CURRENT_AUTH = 0
    return

def current_auth():
    print("Using authentication:" + str(CURRENT_AUTH))

    #return current authentication for use in tweepy.stream(how to reset stream whilst running)
    auths = set_auths(KEY_PAIRS)
    curauth = auths[CURRENT_AUTH]
    return curauth

def db_client():
    # Use twitterdb database. If it doesn't exist, it will be created.
    cl = client[DATABASE_NAME]
    return cl

def check_db():
    #instantiate DB_RUNNING as global
    global DB_RUNNING

    try:
        db_client()
    except errors.ServerSelectionTimeoutError as err:
        print("Could not connect to database: ", err)
        DB_RUNNING = False

    #if database is running and config to drop database is true
    #drop database and print out confirmation
    if IS_DROP and DB_RUNNING == True:
        db_client()[COLLECTION_NAME].remove({})
        print("Successfully dropped collection: remaining check:" + db_client()[COLLECTION_NAME].count())

    if DB_RUNNING == False:
        # todo ask if would like to proceed else exit
        return

def insert_tweet(data):
    try:
        # Decode the JSON from Twitter
        datajson = json.loads(data)

        # grab the 'created_at' data from the Tweet to use for display
        created_at = datajson['created_at']

        if DB_RUNNING == True:

            # insert the data into the mongoDB into a collection called twitter_search
            # if twitter_search doesn't exist, it will be created.
            db_client()[COLLECTION_NAME].insert(datajson)
            #print out a message to the screen that we have collected a tweet
            print("Tweet "+str(db_client()[COLLECTION_NAME].count())+", created at " +str(created_at))
        else:
            # Increment a global integer variable MOCK_COUNT
            # to be used in the mock insert
            global MOCK_COUNT
            MOCK_COUNT += 1
            #Return mocked
            print("Mock: Tweet "+str(MOCK_COUNT)+", created at " +str(created_at))

    except Exception as e:
        print(e)


#Set up the listener. The 'wait_on_rate_limit=True' is needed to help with Twitter API rate limiting.
listener = StreamListener(api=tweepy.API(retry_count=6))
streamer = tweepy.Stream(auth=current_auth(), listener=listener)

#filter the stream utilizing the WORDSas specified
print("Tracking: " + str(WORDS))
streamer.filter(track=WORDS)