from mobile import *
# from algorithm import *
from algorithm_multi_merge import *
from time import time

tl = Timeline(stream_samples())

print len(tl.hierarchy)

if True:
    start = time()
    tl.build_hierarchy()
    duration = time() - start

    print "Completed hierarchy in %.2f seconds" % duration
