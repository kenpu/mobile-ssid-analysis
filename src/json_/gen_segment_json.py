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

readings = mobile.stream_readings()

# Clustering
start = time.time()
H = cluster.Hierarchy(next(readings))
for i, r in enumerate(readings):
    H.append(r)
    # if i % 1000 == 0:
    #     print(i)

print("Clustering duration = %.2f seconds" % (time.time() - start))

# Segmentation
start = time.time()
tops = cluster.segment(H, threshold=0.01)
print("Segmentation duration = %.2f seconds" % (time.time() - start))

# Locations
start = time.time()
locs = cluster.locations(tops, threshold=0.1)
print("Locations duration = %.2f seconds" % (time.time() - start))

def humanize(sec):
    if sec < 60:
        return "%2.2f s" % sec
    min = sec / 60.0
    if min < 60:
        return "%2.2f m" % min
    hr = min / 60.0
    return "%2.2f h" % hr

def print_tops(tops):
    for i,C in enumerate(tops):
        t0, t1, dt = C.timespan()
        n_readings = len(C.readings())
        print("[%3d] %10s - %10s | %10s | %.3d readings" % (
            i, t0, t1, humanize(dt), n_readings))

def print_locations(locs):
    for i,L in enumerate(locs):
        print("======== %d: %s, %d========" % (i, humanize(L.total_duration()),
            len(L.clusters)))
        print(",".join("%s[%.2f]" % (x,y) for x,y in L.ssid_strength()[:3]))

#print_tops(tops)
#print_locations(locs)

print("Adele wants..")

print(cluster.Cluster.timespan(locs[0].clusters[0])[0])
print(locs[0].ssid_strength()[:3][0][0])

data = []
for l in locs:
    location = {}
    location["location"] = ",".join("%s[%.2f]" % (x,y) for x,y in l.ssid_strength()[:3])
    location["segments"] = []
    for c in l.clusters:
        d = {}
        d["start"] = cluster.Cluster.timespan(c)[0]
        d["end"] = cluster.Cluster.timespan(c)[1]
        location["segments"].append(d)
    data.append(location)

print(json.dumps(data, indent=4))
