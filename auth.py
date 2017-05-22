import tweepy
import logging
from config import *

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

