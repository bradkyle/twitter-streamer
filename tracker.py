import time
import tweepy
import itertools
from operator import attrgetter
from multiprocessing import Process
from config import AUTH_PAIRS, WORDS

class TwitterStreamer(object):
        def __init__(self,auth_pairs,term_sets):
            self.auth_pairs = auth_pairs
            self.term_sets = term_sets

            self.auths = self.set_auths()
            self.auth_buffer = 10

        def set_auths(self):
            auths = []
            for consumer_key, consumer_secret, access_key, access_secret in self.auth_pairs:
                single_auth = Auth(consumer_key=consumer_key,consumer_secret=consumer_secret,access_token=access_key,access_token_secret=access_secret).set_auth()
                auths.append(single_auth)
            return auths

        def start_streaming(self):
            for term_set in self.term_sets:
                tracker = Tracker(terms=term_set, collection_name="test")
                process = Process(target=tracker.test())
                process.start()

        def start_twitter_streamer(self):
            print()
            #todo 1) instantiate the set of Trackers in parrellel, with collection name, terms and its name

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

    def __init__(self, terms, collection_name, auths):


        self.terms = terms
        self.collection_name = collection_name
        self.auth_buffer = 100

        self.current_auth = self.get_good_auth()
        self.listener = StreamListener(api=tweepy.API())

    def test(self):
        print("Tracker would be running now")

    def track(self):
        while True:
            try:
                print(str(self.collection_name)+": using authentication " + str(self.current_auth.id))
                streamer = tweepy.Stream(auth=self.current_auth, listener=self.listener)

                # filter the stream utilizing the WORDSas specified
                print("Tracking: " + str(self.terms))
                streamer.filter(track=self.terms)
            except:
                print('An error has occurred whilst track()')
                #todo log error
                continue

    def wait_before_returning_key(self):
        print("There is no key available that is not being used or rate limited, proceeding to wait for one.")

        least_wait_auth = min(self.auths, key=attrgetter('time_left'))
        least_wait_auth_time_left = least_wait_auth.time_left
        time.sleep(least_wait_auth_time_left + self.auth_buffer)

        return least_wait_auth

    def get_good_auth(self):
        # return an auth from the set of auths that isn't being rate limited or used and if one doesn't exist wait for the one with the least time
        # left on the rate limit imposed on it by twitter
        appropriate_key = next((auth for auth in self.auths if auth.being_used and auth.is_rate_limited == False),
                               self.wait_before_returning_key())
        return appropriate_key

    def switch_auth(self):
        self.auth_key = self.get_good_auth()
        return





class StreamListener(tweepy.StreamListener):

    def on_connect(self):
        # Called initially to connect to the Streaming API
        print("You are now connected to the streaming API.")
        # todo run everything that needs to be done before the stream starts

    def on_error(self, status_code):
        print("error has ocurred")

    def on_timeout(self):
        print("timeout has ocurred")

    def on_disconnect(self, notice):
        print("disconnect has ocurred")

    def on_data(self, data):
        print("Recieved data")






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







# def handle_error(status_code):
#     if status_code in [420, 429, 503]:
#
#         err_string = 'Twitter streaming: temporary error occured : ' + repr(status_code)
#         print(err_string)
#         logging.warning(err_string)
#
#
#         switch_auth()
#         return True
#
#
#     elif status_code in [400, 401, 403, 404, 406, 410, 422, 500, 502, 504]:
#
#         err_string = "Twitter streaming: error: " + repr(status_code)
#         print(err_string)
#         logging.warning(err_string)
#
#         try:
#             switch_auth()
#             return False
#
#         except Exception as e:
#
#             err_string = "Could not recover from irremediable error "+str(status_code)+" :"+str(e)
#             print(err_string)
#             logging.critical(err_string)
#
#
#         return False
#
#
#     elif status_code in [200, 304]:
#
#         print("Twitter streaming: " + status_code)
#         #no need to log this
#
#         return True
#
#     else:
#
#         err_string = "Received unknown status: " + repr(status_code)
#         print(err_string)
#         logging.critical(err_string)
#         return False


TwitterStreamer(auth_pairs=AUTH_PAIRS, term_sets=WORDS).start_streaming()