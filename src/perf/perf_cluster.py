import mobile
import cluster
import time
import matplotlib
matplotlib.use('Agg')
from matplotlib import pylab

mobile.DB = "./data/ken.sqlite3"
readings = mobile.stream_readings()
t = []
H = cluster.Hierarchy(next(readings))
for r in readings:
    s = time.time()
    H.append(r)
    t.append((time.time() - s) * 1000)

pylab.title("Incremental segmentation")
pylab.plot(t)
pylab.xlabel("Number of readings in index")
pylab.ylabel("Update time (milliseconds)")
pylab.savefig("incremental.png")
