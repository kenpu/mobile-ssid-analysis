import mobile
from itertools import groupby
from pprint import pprint

print "First few of bssid-readings"
s = mobile.stream_raw_readings()

for i, x in zip(range(5), s):
    print x





print "First few samples"
s = mobile.stream_samples()
for i, x in zip(range(5), s):
    print x["stamp"]


s = mobile.stream_samples()
s2 = mobile.slide_window(s, 2)
for i, x in zip(range(100), s2):
    print "%2d\t %s -- %s = %.2f" % (
            i, 
            x[0]["stamp"], 
            x[1]["stamp"], 
            mobile.sample_similarity(x[0], x[1]))

