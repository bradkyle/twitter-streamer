#WORDS = ['bitcoin']
import logging


#Bitcoin words to filter out of the stream
BITCOIN_WORDS = ['bitcoin', 'btc', '@Bitcoin', '@BitcoinMagazine']

#Ethereum words to filter out of the stream
ETHER_WORDS = ['ether', 'ethereum', 'eth', '@ethereumproject', '@VitalikButerin']

#Ripple words to filter out of the stream
RIPPLE_WORDS = ['ripple', 'xrp', '@Ripple', '@RippleLabs']

#Litecoin words to filter out of the stream
LITECOIN_WORDS = ['litecoin', 'ltc', '@SatoshiLite', '@litecoin']

WORDS = BITCOIN_WORDS

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

IS_MOCK = False

IS_DROP = False
DB_RUNNING = False

MONGO_HOST= "mongodb://mongo:27017"

DATABASE_NAME = "twitter"

logdir = "./log/"
logging.basicConfig(filename=logdir+'info.log',level=logging.INFO)



