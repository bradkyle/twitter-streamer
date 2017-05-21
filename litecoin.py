from twit import streamer

WORDS = ['litecoin']


#filter the stream utilizing the WORDSas specified
print("Tracking: " + str(WORDS))
streamer.filter(track=WORDS)