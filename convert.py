import sys
import tweetdb

ots = tweetdb.TweetStore(sys.argv[1])
nts = tweetdb.TweetStoreSQL(sys.argv[2])

for t in ots.values():
    nts.add(t)
