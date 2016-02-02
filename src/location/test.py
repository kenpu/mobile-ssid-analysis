import mobile
from itertools import groupby
from pprint import pprint

print "First few of bssid-readings"
s = mobile.stream_raw_samples()

for i, x in zip(range(5), s):
    print x





print "First few readings"
s = mobile.stream_readings()
for i, x in zip(range(5), s):
    print x["stamp"]


s = mobile.stream_readings()
s2 = mobile.slide_window(s, 2)
for i, x in zip(range(100), s2):
    print "%2d\t" % i, x[0]["stamp"], " -- ", x[1]["stamp"], " = ", mobile.reading_similarity(
            x[0], x[1])

