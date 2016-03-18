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



print(cluster.Cluster.timespan(locs[0].clusters[0])[0])
print(locs[0].ssid_strength()[:3][0][0])

#####################################################
#
# Recreate the timeline with { start, end, location }
#
########################################################
timeline = []      # need to recreate the timeline
locations = {}     # generate a dictionary of locations
location_id = 0
for l in locs:
    location_name = ",".join("%s[%.2f]" % (x,y) for x,y in l.ssid_strength()[:3])
    locations[location_id] = {"id": location_id, "name": location_name, "count": len(l.clusters)}

    for c in l.clusters:
        start = cluster.Cluster.timespan(c)[0]
        end = cluster.Cluster.timespan(c)[1]
        timeline.append({
            "start": start[0:10]+"T"+start[11:16],
            "end": end[0:10]+"T"+end[11:16],
            "location": location_id})

    location_id += 1

timeline.sort(key=lambda x: x["start"])

# time to count transitions!
transitions = [[0 for x in range(len(locations))] for x in range(len(locations))]   # [from][to] value is the count
for i in range(0, len(timeline)-2):
    transitions[timeline[i]["location"]][timeline[i+1]["location"]] += 1

transition_json = []
#  make json friendly transition data
for i in range(0, len(transitions)-1):
    for j in range(0, len(transitions)-1):
        if transitions[i][j] > 0:
            transition_json.append({"source": i, "target": j, "value": transitions[i][j]})


# make json friendly location
location_json = []
for key, value in locations.items():
    location_json.append(value)


data = {"locations": location_json, "transitions": transition_json}

print(json.dumps(data, indent=4))

with open("location_transition.json", "w") as outfile:
    json.dump(data, outfile)

