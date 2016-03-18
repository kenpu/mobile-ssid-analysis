import mobile
import cluster
import itertools
import time
import sys

def pre_analyze(db):
    result = dict()

    mobile.DB = db
    readings = mobile.stream_readings()

    start = time.time()
    H = cluster.Hierarchy(next(readings))
    for i, r in enumerate(readings):
        H.append(r)

    movements = cluster.segment(H, threshold=0.01)

    locs = cluster.locations(movements, threshold=0.1)

    return (H, movements, locs)

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
