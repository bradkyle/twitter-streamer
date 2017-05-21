from twit import streamer

WORDS = ['dash']


#filter the stream utilizing the WORDSas specified
print("Tracking: " + str(WORDS))
streamer.filter(track=WORDS)