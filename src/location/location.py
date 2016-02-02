from mobile import *

readings = stream_readings()

for (i, (x, y)) in enumerate(slide_window(readings, 2)):
    t1 = x["stamp"]
    t2 = y["stamp"]
    n1 = len(x["readings"])
    n2 = len(y["readings"])
    sim = reading_similarity(x, y)
    print "%.4d: %s(%d) -- %s(%d) = %.2f" % (i, t1, n1, t2, n2, sim)
