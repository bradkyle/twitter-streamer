import json
import time

from pymongo import MongoClient, errors
import tweepy
import itertools
import multiprocessing
import logging
from operator import attrgetter
from bs4 import BeautifulSoup as Soup
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

#======================================================================================================================>
#
#======================================================================================================================>


# TRACKERS = [
#     ["bitcoin",['bitcoin', 'btc', '@Bitcoin', '@BitcoinMagazine']],
#     ["ether",['ether', 'ethereum', 'eth', '@ethereumproject', '@VitalikButerin']],
#     ["ripple",['ripple', 'xrp', '@Ripple', '@RippleLabs']],
#     ["litecoin",['litecoin', 'ltc', '@SatoshiLite', '@litecoin']],
#     ["litecoin",['litecoin', 'ltc', '@SatoshiLite', '@litecoin']]
#     ["litecoin",['litecoin', 'ltc', '@SatoshiLite', '@litecoin']]
#     ["litecoin",['stellar lumens', 'ltc', '@SatoshiLite', '@litecoin']]
#
# ]

#slimmed down tracking terms to decrease variability
TRACKERS = [
    ["bitcoin",['bitcoin']], #check
    ["ether",['ether', 'ethereum']], #
    ["ripple",['ripple']], #
    ["litecoin",['litecoin']], #has exited with exception: HTTPSConnectionPool
    ["bytecoin",['bytecoin']], #
    ["monero",['monero']], #
    ["lumens", ['stellar lumens']], #
    ["dogecoin", ['dogecoin']], #
    ["siacoin", ['siacoin']], #
    ["stratis", ['stratis']], #
]

#each auth pair can support 2 trackers on average
AUTH_PAIRS = [  # consumer key                consumer secret                                       access token                                          access token secret
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

#todo email critical errors and or log reports on a regular basis

IS_MOCK = True
IS_DROP = False
DB_USERNAME  = ""
DB_PASSWORD  = ""

MONGO_HOST= "mongodb://mongo:27017"

DATABASE_NAME = "twitter"

logging.basicConfig(filename='./log/info.log',level=logging.INFO)
formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s")

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
                #todo might be redundancy

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

        #Applying attribute to an external class without hard coding it
        self.listener.tracker_instance = self


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
            except Exception as e:
                print("The streaming process for tracker " +self.collection_name+ " has exited with exception: "+ str(e))
                logging.warning("The streaming process for tracker " +self.collection_name+ " has exited with exception: "+ str(e))
                raise

    def switch_rate_limited_auth(self):
        #change status of Auth to is_rate_limited = True
        self.current_auth.is_being_rate_limited()

        #get an Auth instance that isn't being rate limited
        #todo switch key to being used or don't based on config (i.e. how many processes can auth be used for)
        self.current_auth = self.auths_instance.get_good_auth()
        print("Auth has been switched to :" + str(self.current_auth.id))

        #restart tracking process recursively
        self.track()


    def handle_error(self, status_code):

        #420: Returned when an application is being rate limited
        #429: Application rate limit has been exhausted for the resource.
        #503: The Twitter servers are up, but overloaded with requests. Try again later.
        if status_code in [420, 429, 503]:

            print('Twitter streaming: temporary error occured : ' + repr(status_code))
            self.switch_rate_limited_auth()
            return True

        #fatal errors, stop and log critical
        elif status_code in [400, 401, 403, 404, 406, 410, 422, 500, 502, 504]:
            #todo attempt to recover perhaps
            err_string = "Twitter streaming: error: " + repr(status_code)
            print(err_string)

        #everything is Ok, no need to log this
        elif status_code in [200, 304]:
            return True

        else:
            #todo recover from unknown status
            err_string = "Received unknown status: " + repr(status_code)


# In-built Class provided by Tweepy
class StreamListener(tweepy.StreamListener):

    # Called initially to connect to the Streaming API
    def on_connect(self):
        msg = str(self.tracker_instance.collection_name) + ": Connected to the streaming API."
        print(msg)
        logging.info(msg)

    # Called when an error occurs whilst streaming
    def on_error(self, status_code):
        self.tracker_instance.handle_error(status_code)

    #called on timeout
    #todo recover from timeout
    def on_timeout(self):
        print("timeout has ocurred")
        logging.critical("A timeout has occured")

    #called if disconnected
    def on_disconnect(self, notice):
        self.tracker_instance.handle_error(notice)

    #called when data recieved
    def on_data(self, data):
        self.tracker_instance.store_collection_instance.insert_tweet(data)




class Auths(object):
    """
         A authentication key/token/OauthHandler node instance

         Attributes:
            auth_pairs: Is the authentication key/token sets provided in the config part of the program
            auth_instances: Refers to the instances of Auth 
            auths: refers to OauthHandler instances for respective instances of Auth
            auth_buffer: the time to add onto rate limit time before returning a valid OauthHandler (least_wait_auth)
    """

    def __init__(self, auth_pairs):
        self.auth_pairs = auth_pairs
        self.auth_instances = Auth.instances
        self.auths = []
        self.auth_buffer = 100


        #loops through all key sets given and instantiates an Auth for it
        self.instantiate()

    #The instantiate function loops through all auth pairs provided to it by the auth pairs array
    #and uses its respective consumer_key, consumer_secret, access_key and access_secret to create
    #an Auth instance for however many twitter key/token pairs are provided
    def instantiate(self):
        auth_pairs_count = 0
        for consumer_key, consumer_secret, access_key, access_secret in self.auth_pairs:
            Auth(consumer_key=consumer_key, consumer_secret=consumer_secret, access_token=access_key, access_token_secret=access_secret)
        print("authentication sets instantiated.")
        logging.info("Instantiated all auth_pairs in Auth instances")

    #Provided there are no keys that are not being used or rate limited
    #this function gets the Auth instance with the least amount of time left before
    #its is_rate_limited = True status is lifted and returns it after that wait time has ended
    #effectively pausing the stream for the Tracker in reference until this time.sleep() has completed
    def wait_before_returning_key(self):
        print("There is no key available that is not being used or rate limited, proceeding to wait for one.")
        logging.warning("There is no key available that is not being used or rate limited, proceeding to wait for one.")

        least_wait_auth = min(self.auth_instances, key=attrgetter('time_left'))
        least_wait_auth_time_left = least_wait_auth.time_left
        time.sleep(least_wait_auth_time_left + self.auth_buffer)

        return least_wait_auth

    #return an auth from the set of auths that isn't being rate limited or
    #used and if one doesn't exist wait for the one with the least time
    #left on the rate limit imposed on it by twitter and accounted for by time_lift
    def get_good_auth(self):
        try:
            appropriate_auth = next((auth for auth in self.auth_instances if ( auth.being_used + auth.is_rate_limited ) == 0))
        except StopIteration:
            appropriate_auth = self.wait_before_returning_key()
        return appropriate_auth




class Auth(object):
    #adds an id to every new auth instance
    newid = itertools.count().next

    instances = []
    auths_being_rate_limited = []

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
            rate_limit_wait_time: Is the set amount of time that the is_rate_limited == True status lasts for
            time_left: Is the amount of time that the is_rate_limited == True has left
            time_done: The amount of time that has passed since the Auth was rate limited
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
        self.rate_limit_wait_time = 15 * 60 #todo add buffer to 15 minutes

        if self.is_rate_limited == True:
            self.time_done = time.time() - self.last_rate_limited
            self.time_left = self.rate_limit_wait_time - self.time_done

        #appends current auth instance to
        #auth instance array so that it can be looped through dynamically
        Auth.instances.append(self)

    #This method changes the Auth is_rate_limited= True and sets the last_rate_limited time to now,
    #it also appends the specified Auth to the auths_being_rate_limited array in order so that it
    #may be changed back to is_rate_limited = False after the alloted time interval has been completed
    def is_being_rate_limited(self):
        self.is_rate_limited = True
        self.last_rate_limited = time.time()
        Auth.auths_being_rate_limited.append(self)
        logging.info("Authentication set has been rate limited at %s" % str(time.time()))

    #This method loops through all rate limited keys stored in the auths_being_rate_limited array
    #and sets the is_rate_limit status to False if it has been more that 15 minutes + buffer
    #this could be improved by running a check using the rate_limit_status_function provided
    #by tweepy
    #todo check tweepy rate_limit_status()
    def check_rate_limit_status(self):
        for rate_limited_auth in self.auths_being_rate_limited:
            if self.time_done > self.rate_limit_wait_time:
                rate_limited_auth.is_rate_limited = False
                logging.info("Rate limited has been lifted on Auth instance with consumer key %s", self.consumer_key)

    #This method takes in the auth keys/tokens for the specified instance and converts
    #them to a tweepy.OAuthHandler before returning it
    def set_auth(self):
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        return auth




class Tweetstore(object):
    """
         The database store used for the application.  

         Attributes:
            db_name: Is the database name that should be used
            db_host: is the host url of the database that should be used
            db_mock: Is set to true when we dont want the database to be in use
            db_username: Username for database
            db_password: Password for the database
            db_is_drop: Must the database be dropped every time the application is started
            db_running: A boolean value specifying wheteher or not the database is running
            pymongo_client: Is the pymongo client instance
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
            logging.error("Could not connect to database: %s" % e)
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
                logging.error("Could not drop database: %s" % e)
            else:
                print("Successfully dropped database.")
                logging.info("Successfully dropped database.")



class StoreCollection(object):

    """
             The database store used for the application.  

             Attributes:
                collection_name: Twitter api consumer key.
                store_instance: This refers to the class instance of TweetStore
                pymongo_client: This refers to the connection instance with pymongo  
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

    #recieve data from tweepy and insert into db instance
    def insert_tweet(self, data):
        # Decode the JSON from Twitter
        datajson = json.loads(data)

        #check if database is running, then try to insert else
        if self.store_instance.db_running == True:
            try:
                self.db_collection.insert(datajson)
            except Exception as e:
                logging.error("An error has occured whilst trying to insert a tweet into the database: %s" % e)
            else:
                self.collection_tweet_count += 1
                print(self.collection_name + ": Tweet " + str(self.collection_tweet_count) + ", successfully added to collection")
        else:
            self.mock_count += 1
            print(self.collection_name +"(Mock) : Tweet " + str(self.mock_count) + ", successfully added to collection")

    def all_collection_tweets(self):
        if self.store_instance.db_mock != True and self.store_instance.db_running == True:
            cursor =  self.db_collection.find({})
            return cursor


class Email(object):

    fromaddr = "YOUR ADDRESS"
    password = "YOUR PASSWORD"
    smtp_address = "smtp.gmail.com"
    smtp_port = 587
    toaddr = "ADDRESS YOU WANT TO SEND TO"
    msg = MIMEMultipart('alternative')
    msg.preamble = """Your mail reader does not support the report format."""

    html = """
    <html>
      <head></head>
      <body>
        <p>Hi!<br>
           How are you?<br>
           Here is the <a href="http://www.python.org">link</a> you wanted.
        </p>
      </body>
    </html>
    """

    def __init__(self):
        self.subject = "SUBJECT OF THE MAIL"
        self.text = ""


    def send(self):
        self.msg['From'] = self.fromaddr
        self.msg['To'] = self.toaddr
        self.msg['Subject'] = self.subject


        html = MIMEText(self.html, 'html')
        self.msg.attach(html)

        server = smtplib.SMTP(self.smtp_address, self.smtp_port)


    def format_email(self):
        print()






TwitterStreamer(auth_pairs=AUTH_PAIRS, trackers=TRACKERS).start_streaming()