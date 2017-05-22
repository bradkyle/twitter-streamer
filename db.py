from pymongo import MongoClient, errors
from config import *
import json


#todo complete database client
class TweetStore(object):

      """
              A twitter key set  

              Attributes:
                 dbname: All Twitter authentication keys/tokens/secrets.
                 host_url: All Twitter authentication sets.
                 db_is_running: All Twitter authentication sets.
                 is_drop: All Twitter authentication sets.
      """

      def __init__(self, dbname, host_url):
          self.dbname = dbname
          self.host_url = host_url

          self.db_running = False
          self.is_drop = True

      def sdb(self):
          try:
             dbconn = pymongo.MongoClient(self.dbname)[self.host_url]
             self.db_running = True
          except pymongo.errors.ConnectionFailure:
             print ("Could not connect to server: %s" % pymongo.errors.ConnectionFailure)
             self.db_running = False
          return dbconn

      def is_drop_check(self):


      def check_db(self):

          if self.db_running == False:
              response = input("The database is not running or the connection was unsuccessfull. Would you like to proceed with a mocked example? (Press Enter to continue): ")
              return

          # if database is running and config to drop database is true
          # drop database and print out confirmation
          if self.is_drop and self.db_running == True:
              self.sdb[COLLECTION_NAME].remove({})
              print("Successfully dropped collection: remaining check:" + db_client()[COLLECTION_NAME].count())



      def insert_tweet(self, data):
          try:
              # Decode the JSON from Twitter
              datajson = json.loads(data)

              # grab the 'created_at' data from the Tweet to use for display
              created_at = datajson['created_at']

              if self.db_running == True:

                  # insert the data into the mongoDB into a collection called twitter_search
                  # if twitter_search doesn't exist, it will be created.
                  db_client()[COLLECTION_NAME].insert(datajson)
                  # print out a message to the screen that we have collected a tweet
                  print("Tweet " + str(db_client()[COLLECTION_NAME].count()) + ", created at " + str(created_at))
              else:
                  # Increment a global integer variable MOCK_COUNT
                  # to be used in the mock insert
                  global MOCK_COUNT
                  MOCK_COUNT += 1
                  # Return mocked
                  print("Mock: Tweet " + str(MOCK_COUNT) + ", created at " + str(created_at))

          except Exception as e:
              print(e)

      def all_collection_tweets(self, collection):
          try:
              print("")
          except:
              print()

      def all_tweets(self):
          try:
              print("")
          except:
              print()