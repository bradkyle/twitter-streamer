from __future__ import print_function
import tweepy
import logging
import json
from pymongo import MongoClient, errors

#WORDS = ['bitcoin']

KEY_PAIRS = [
    ["WM1MVD31TRGZBiNbXO54p4Sni", "SJzN8rhCSyyzxt55shwpPScX1aEdOWX63q8d8yKC9gNAESsCjO", "367687040-UzRMSNmwLjgjDl3CwAS72UbyeSkDOmKTKzmWSK89", "TAAu1ScD4pscR8nHTp3UyXx2T6JyCqOy5vTmcIYMtuGga"],
    ["qnv3th6JUVEvTDoSHl5YcoYLl", "whgIR7PGf4zmlnlBaTQCIVPAudVBk1Tej93N0xW0vIpavjpQ6W", "863416332095823872-LywT0OQYLI9smMDVDlTG6S9ygj8TA2x", "t6lYoMidHEumwiypurUArSzMMrn3VNQDXRsfXIANzZBsV"],     #yomamas house dc
    ["ghlSi83iK8b6Gt5r40Y5PB3Lh", "kSJkkeB3ggT0oErZ7xPyLOBWOOQytgmJPXao9pfhEnLXWXfyfn", "367687040-P0WS0qnFihACmKdJNHo4m2tVy6LbUakZsLD7mse1", "Z30IzyTEKo4Tedk4fTazhJsz4YihtqY7NkKwoPAHGARYv"], 	#LitmusB bd
    ["OVxT26UmJtdMLlJFY0vNDchRG", "c6iGLYINqU93qehJ9v84M1hVNXtmQGxtz6Pjs7aLO9X2aQh8aR", "860540303421448193-RkErbZqOLToJQtxwk6oV5UhMEb7C9Uq", "VdOlI89dDaLYhCGXYZycWDAuGbVnklCbXyejpiSkziObK"], 	#fart sweat nw
    ["ONoSdnInA2MHk5swW1FiGHBNl", "5pEwoWz97OE8BVTogM1nxtHfdkSjPkZkzAektGt8QAHGojkNuo", "804937531749974016-ChkHvQwqOtsX1pKPnQRa4MqdGngXMTA", "OG7dxmYBD63749upwQRvSeJlafyJP6gW7SRWpJdWpMpYb"], 	#twitterydo sm
    ["kIFURn1JdN2k1w0WUgENYz8w1", "8djbRqNF9Pg7J7Ofjv2tdXbObEWazrr4xt8FxWKMiev8qwhexb", "860540303421448193-XJt9pKmqUye0yPXkSlm49LEtFHQ7lQW", "EiiuRn97OKEt4KXW7SQfmXvVjkR1Ec3ZHmTi1luRIUmKI"], 	#slapping babies nw
    ["Zv9zY9KWONeU3qKbShxq9Oat9", "Uotuon99K26RCxtUkgB7KIBMjIKLaEQ8CFoCikCkqmDAstJCBX", "860540303421448193-IgRs21k3HerMXA7eU97S90BZ3C460kF", "ab1WSco1X6jzmhNRNAnD1ieF7wmYGAKwK3ZbixwgyjuON"], 	#bearsweat nw
    ["SpPvOhlmtNM3vDzK67XxT6r4A", "QvkZjhp4YnmpnE2bZpvsHe0HYwbuNonMLgplgQKbV3NUOfaOHH", "804937531749974016-BynNs2n2PaK2VTvg0YlK92aBcArd9dr", "wvQ6jiey1T6ORhIwHZm3rMJi5UdRQTQgijHtqRUy9Xn7L"], 	#slappity fart face sm
    ["gtyPPsUvl94WPsevhBMm1xGQ2", "lgVN2CFlsXdVthgt4ZdVv1ExQNwCX2zdqv2rWkZ7ccpjkbuVG5", "863416332095823872-MyeGXCHVAWwgQG93rCtIKpxS7444bou", "cDr0TZ7dHzx0HVzCdpLfkivyRjl2dDvYjXHkaXOxa2vp6"], 	#sauce force dc
    ["Zv9zY9KWONeU3qKbShxq9Oat9", "Uotuon99K26RCxtUkgB7KIBMjIKLaEQ8CFoCikCkqmDAstJCBX", "860540303421448193-IgRs21k3HerMXA7eU97S90BZ3C460kF", "ab1WSco1X6jzmhNRNAnD1ieF7wmYGAKwK3ZbixwgyjuON"],
]


# CURRENT_AUTH counts the number of auth sets have been changed out due to a rate limit
CURRENT_AUTH = 0

MOCK_COUNT = 0

IS_MOCK = False

IS_DROP = False
DB_RUNNING = False

MONGO_HOST= "mongodb://mongo:27017"
client = MongoClient(MONGO_HOST)

DATABASE_NAME = "twitter"
COLLECTION_NAME = "bitcoin"

logdir = "./log/"
logging.basicConfig(filename=logdir+'info.log',level=logging.INFO)

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

#todo test handle error
def handle_error(status_code):
    if status_code in [420, 429, 503]:

        err_string = 'Twitter streaming: temporary error occured : ' + repr(status_code)
        print(err_string)
        logging.warning(err_string)


        switch_auth()
        return True


    elif status_code in [400, 401, 403, 404, 406, 410, 422, 500, 502, 504]:

        err_string = "Twitter streaming: error: " + repr(status_code)
        print(err_string)
        logging.warning(err_string)

        try:
            switch_auth()
            return False

        except Exception as e:

            err_string = "Could not recover from irremediable error "+str(status_code)+" :"+str(e)
            print(err_string)
            logging.critical(err_string)


        return False


    elif status_code in [200, 304]:

        print("Twitter streaming: " + status_code)
        #no need to log this

        return True

    else:

        err_string = "Received unknown status: " + repr(status_code)
        print(err_string)
        logging.critical(err_string)
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

#todo test switch auth
def switch_auth():

    err_string = "Attempting to switch authentication."
    print(err_string)
    logging.info(err_string)

    previous_auth = CURRENT_AUTH

    # Increment a global integer variable CURRENT_AUTH
    # used to track/index the current authentication
    global CURRENT_AUTH
    CURRENT_AUTH += 1
    if CURRENT_AUTH >= len(KEY_PAIRS) :
        CURRENT_AUTH = 0

    print("Successfully updated key: "+str(previous_auth)+" to key: "+str(CURRENT_AUTH))

    return

#todo test current auth
def current_auth():
    print("Using authentication:" + str(CURRENT_AUTH))

    #return current authentication for use in tweepy.stream(how to reset stream whilst running)
    auths = set_auths(KEY_PAIRS)
    curauth = auths[CURRENT_AUTH]
    return curauth

#todo test db connection
def db_client():
    # Use twitterdb database. If it doesn't exist, it will be created.
    cl = client[DATABASE_NAME]
    return cl

#todo test checkdb
def check_db():
    #instantiate DB_RUNNING as global
    global DB_RUNNING

    if DB_RUNNING == True:
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

#todo test insert tweet
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
# print("Tracking: " + str(WORDS))
# streamer.filter(track=WORDS)