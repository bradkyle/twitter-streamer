from twit import streamer

WORDS = ['NEM']


#filter the stream utilizing the WORDSas specified
print("Tracking: " + str(WORDS))
streamer.filter(track=WORDS)