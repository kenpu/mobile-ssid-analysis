import mobile
import cluster
import itertools
import time
import sys
import json

if sys.argv[1:]:
    mobile.DB = sys.argv[1]
else:
    print("Usage: %s <db>" % sys.argv[0])
    sys.exit()


#  A point is { "reading": ---, "time": ---- }
points = []

readings = mobile.stream_readings()

# Clustering
#  start = time.time()
H = cluster.Hierarchy(next(readings))
#  points.append({"readings": 1, "time": (time.time()-start)*1000})

threshold = 200
for i, r in enumerate(readings):
    start = time.time()
    H.append(r)
    end = time.time()
    span = (end-start)*1000
    if i % 10 == 0 and span < threshold:
        points.append({"readings": i, "time": span})


data = {"title": "Incremental Hierarchical Clustering",
        "yaxis": "Time (milliseconds)",
        "xaxis": "Reading Added",
        "data": points}


print(json.dumps(data, indent=4))

with open("hierarchical_cluster_time.json", "w") as outfile:
    json.dump(data, outfile)


