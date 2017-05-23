import json
import time

from pymongo import MongoClient, errors
import tweepy
import itertools
import multiprocessing
import logging
from operator import attrgetter

TRACKERS = [
    ["bitcoin",['bitcoin', 'btc', '@Bitcoin', '@BitcoinMagazine']],
    ["ether",['ether', 'ethereum', 'eth', '@ethereumproject', '@VitalikButerin']],
    ["ripple",['ripple', 'xrp', '@Ripple', '@RippleLabs']],
    ["litecoin",['litecoin', 'ltc', '@SatoshiLite', '@litecoin']]
]

AUTH_PAIRS = [
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

IS_MOCK = True
IS_DROP = False
DB_USERNAME  = ""
DB_PASSWORD  = ""

MONGO_HOST= "mongodb://mongo:27017"

DATABASE_NAME = "twitter"

logdir = "./log/"
logging.basicConfig(filename=logdir+'info.log',level=logging.INFO)

#todo check if input is blank or does not fit requirement

class TwitterStreamer(object):
        """
         Uses multiprocessing to stream the results for a set of twitter search terms   

         Attributes:
            name: The name of the tracker that shows in the terminal log.
            terms: The array of terms that will be filtered out from the twitter stream.
            collection_name: The name of the db collection that will be used to store the tweets returned from this tracker.
            current_key: The current_key references the current key set that is in use (i.e. its index).
            
        """

        def __init__(self,auth_pairs,trackers):
            self.a_pairs = auth_pairs
            self.trackers = trackers
            self.auths_instance = Auths(self.a_pairs)

        def start_streaming(self):
            processes = []

            for tracker in self.trackers:
                tracker = Tracker(terms=tracker[1], collection_name=tracker[0], auths_instance=self.auths_instance)

                p = multiprocessing.Process(target=tracker.track)
                processes.append(p)

            for p in processes:
                p.start()


class Tracker(object):


    """
     A twitter stream term set tracker   
    
     Attributes:
        name: The name of the tracker that shows in the terminal log.
        terms: The array of terms that will be filtered out from the twitter stream.
        collection_name: The name of the db collection that will be used to store the tweets returned from this tracker.
        current_key: The current_key references the current key set that is in use (i.e. its index).
        collection_count: The number of documents in the collection.
        key_set_array: The multidimensional array of keys that will be used in this tracker instance.
        keys: All Twitter authentication keys/tokens/secrets.
        auths: All Twitter authentication sets.
        auth_buffer: the buffer time to wait and try the best available key
    """

    def __init__(self, terms, collection_name, auths_instance):
        self.auths_instance = auths_instance
        self.terms = terms
        self.collection_name = collection_name
        self.current_auth = self.auths_instance.get_good_auth()
        self.listener = StreamListener(api=tweepy.API())

        self.store_collection_instance = StoreCollection(collection_name)

        self.listener.tracker_instance = self
        self.db_instance = Tweetstore()

    def track(self):
        while True:
            try:
                streamer = tweepy.Stream(auth=self.current_auth.set_auth(), listener=self.listener)

                self.current_auth.being_used = True
                if self.current_auth.being_used == True:
                     print(str(self.collection_name)+": using authentication " + str(self.current_auth.id))

                # filter the stream utilizing the WORDSas specified
                print("Tracking: " + str(self.terms))
                streamer.filter(track=self.terms)
            except:
                print('An error has occurred whilst track()')
                #todo log error
                # continue
                raise

    def switch_auth(self):
        self.current_auth.is_rate_limited = True
        self.current_auth = self.auths_instance.get_good_auth()
        print("auth has been switched to :" + str(self.current_auth.id))
        self.track()

    def handle_error(self, status_code):
        if status_code in [420, 429, 503]:

            err_string = 'Twitter streaming: temporary error occured : ' + repr(status_code)
            print(err_string)
            self.switch_auth()
            return True

        elif status_code in [400, 401, 403, 404, 406, 410, 422, 500, 502, 504]:

            err_string = "Twitter streaming: error: " + repr(status_code)
            print(err_string)

        elif status_code in [200, 304]:

            print("Twitter streaming: " + status_code)
            #no need to log this

            return True

        else:

            err_string = "Received unknown status: " + repr(status_code)



class StreamListener(tweepy.StreamListener):

    def on_connect(self):
        # Called initially to connect to the Streaming API
        print("You are now connected to the streaming API.")

    def on_error(self, status_code):
        print(status_code)
        self.tracker_instance.handle_error(status_code)
        return True

    def on_timeout(self):
        print("timeout has ocurred")

    def on_disconnect(self, notice):
        print("disconnect has ocurred")

    def on_data(self, data):
        self.tracker_instance.store_collection_instance.insert_tweet(data)




class Auths(object):

    def __init__(self, auth_pairs):
        self.auth_pairs = auth_pairs
        self.auth_instances = Auth.instances
        self.auths = []
        self.auth_buffer = 100

        #loops through all key sets given and instantiates an Auth for it
        self.instantiate()

    def instantiate(self):
        for consumer_key, consumer_secret, access_key, access_secret in self.auth_pairs:
            Auth(consumer_key=consumer_key, consumer_secret=consumer_secret, access_token=access_key, access_token_secret=access_secret)
        print("authentication sets instantiated.")

    def wait_before_returning_key(self):
        print("There is no key available that is not being used or rate limited, proceeding to wait for one.")

        least_wait_auth = min(self.auth_instances, key=attrgetter('time_left'))
        least_wait_auth_time_left = least_wait_auth.time_left
        time.sleep(least_wait_auth_time_left + self.auth_buffer)

        return least_wait_auth

    def get_good_auth(self):
        # return an auth from the set of auths that isn't being rate limited or used and if one doesn't exist wait for the one with the least time
        # left on the rate limit imposed on it by twitter
        try:
            appropriate_auth = next((auth for auth in self.auth_instances if ( auth.being_used + auth.is_rate_limited ) == 0))
        except StopIteration:
            appropriate_auth = self.wait_before_returning_key()
        return appropriate_auth





class Auth(object):
    newid = itertools.count().next
    instances = []

    """
         A twitter key set  

         Attributes:
            consumer_key: Twitter api consumer key.
            consumer_secret: Twitter api consumer secret.
            access_token: Twitter api access token.
            access_token_secret:  Twitter api access token secret.
            being_used: Is a boolean value specifying if the Key is being used.
            is_rate_limited: Is a boolean value specifying if the key is currently being rate limited.
            last_rate_limited: Is a time reference to the last time the key was rate limited (used for checking its availability).
            id: The key id.
    """

    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret

        self.being_used = False
        self.is_rate_limited = False
        self.last_rate_limited = 0
        self.id = Auth.newid()

        self.time_left = self.time_left_in_rate_limit()

        Auth.instances.append(self)

    def time_left_in_rate_limit(self):
        time_left = time.time() - self.last_rate_limited
        return time_left

    def is_being_rate_limited(self):
        self.is_rate_limited = True
        self.last_rate_limited = time.time()
        # todo log and print status

    def check_rate_limit_status(self):
        # todo check if twitter is still rate limiting
        print()

    def set_auth(self):
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        return auth

        # todo add a method that switches is being used to true when being used



class Tweetstore(object):
    """
         The database store used for the application.  

         Attributes:
            consumer_key: Twitter api consumer key.
            consumer_secret: 
    """

    def __init__(self):
        self.db_name = DATABASE_NAME
        self.db_host = MONGO_HOST
        self.db_mock = IS_MOCK
        self.db_username = DB_USERNAME
        self.db_password = DB_PASSWORD
        self.db_is_drop = IS_DROP

        self.db_running = False

        if self.db_mock != True:
            self.pymongo_client = self.db_client()



    def db_client(self):
        # if self.
        try:
            client = MongoClient(self.db_host, serverSelectionTimeoutMS=1)

            #force connection on a request as the
            # connect=True parameter of MongoClient seems
            # to be useless here
            client.server_info()

        except errors.ServerSelectionTimeoutError as e:
            print(e)
            if raw_input('Press enter to continue: '):
                self.db_mock = True
                return
        else:
            self.db_running = True
            return client

    def db_if_drop(self):
        if self.db_is_drop and self.db_running == True:
            try:
                self.pymongo_client.drop_database(self.db_name)
            except Exception as e:
                print("Could not drop database: ", e)
            else:
                print("Successfully dropped database.")




class StoreCollection(object):

    """
             The database store used for the application.  

             Attributes:
                collection_name: Twitter api consumer key.
                store_instance: This refers to the classs instance of TweetStore
                pymongo_client: This refers to the connectioninstance with pymongo  
                db_collection: This is the pymongo instance of the class
                collection_tweet_count:The amount of tweets in the collection
                mock_count: The number of mock tweets that have been collected
                
    """

    store_instance = Tweetstore()
    if store_instance.db_mock != True:
        pymongo_client = store_instance.db_client()


    def __init__(self, collection_name):
        self.collection_name = collection_name
        self.mock_count = 0
        if self.store_instance.db_mock != True:
            self.db_collection = self.pymongo_client[self.collection_name]
            self.collection_tweet_count = self.db_collection.count()



    def insert_tweet(self, data):
        # Decode the JSON from Twitter
        datajson = json.loads(data)

        if self.store_instance.db_running == True :
            try:
                self.db_collection.insert(datajson)
            except Exception as e:
                print(e)
                #todo log error and recover
            else:
                self.collection_tweet_count += 1
                print(self.collection_name + ": Tweet " + str(self.collection_tweet_count) + ", successfully added to collection")
        else:
            self.mock_count += 1
            print(self.collection_name +"(Mock) : Tweet " + str(self.mock_count) + ", successfully added to collection")

    def all_collection_tweets(self):
        print() #todo get all tweets from collection



TwitterStreamer(auth_pairs=AUTH_PAIRS, trackers=TRACKERS).start_streaming()