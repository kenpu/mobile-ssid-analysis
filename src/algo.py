import mobile
import cluster
import itertools
import time
import sys
from collections import defaultdict
import random
import json

def pre_analyze(db):
    result = dict()

    mobile.DB = db
    readings = mobile.stream_readings()

    start = time.time()
    H = cluster.Hierarchy(next(readings))
    for i, r in enumerate(readings):
        H.append(r)

    movements = cluster.segment(H, threshold=0.01)
    locs = cluster.locations(movements, threshold=0.5)

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

class Vertex(object):
    def __init__(self, parent, locs=None, children=None):
        self.parent   = parent
        self.children = None
        self.locs     = None
        self.__ssids_cache__ = None

        if loc:
            self.locs = locs
        if children:
            self.children = []
            for c in children:
                self.add_child(c)

    def is_leaf(self):
        return not self.locs == None

    def is_root(self):
        return self.parent == None

    def ssids(self):
        K = 3
        if self.__ssids_cache__:
            return self.__ssids_cache__

        result = defaultdict(float)

        if self.is_leaf():
            for loc in self.locs:
                for k,v in loc.ssid_strength[:K]:
                    result[k] += v
        else:
            for c in self.children:
                for k,v in c.ssids():
                    result[k] += v

        self.__ssids_cache__ = result
        return result

    def common_ssids(self):
        if self.is_leaf():
            return self.ssids().keys()
        else:
            result = None
            for c in self.children:
                if result == None:
                    result = c.ssids().keys()
                else:
                    result = result & c.ssids().keys()
            return result

    def add_child(self, v):
        assert(not self.is_leaf())
        v.parent = self
        self.children.append(v)

    def intersect(self, another):
        x = self.ssids()
        y = another.ssids()
        return len(x & y)

def closest(X):
    I, J = None, None
    c = 0
    for i in range(len(X)):
        x = X[i]
        for j in range(i+1, len(X)):
            y = X[j]
            c_ij = x.intersect(y)
            if I == None or c_ij > c:
                I, J = i, j
                c = c_ij
    return I,J,c

def agglomerative(locs):
    groupby = defaultdict(list)
    K = 3
    for loc in locs:
        tops = loc.ssid_strength()[:K]
        key = tuple(sorted([x[0] for x in tops]))
        groupby[key].append(loc)

    X = [Vertex(None, locs=locs) for locs in groupby.values()]

    return X

    while len(X) > 1:
        I, J, c = closest(X)
        print(len(X), I, J, c)
        if c == 0:
            break
        else:
            u,v = X[I], X[J]
            w = Vertex(None, children=[u, v])
            X[I] = w
            X[J:J+1] = []
    return X

def print_agg(X=None, v=None, indent=""):
    if X:
        for v in X:
            print_agg(v=v)
    elif v:
        print("%s[%s]" % (indent, "|".join(v.common_ssids())))
        if not v.is_leaf():
            for c in v.children:
                print_agg(v=c, indent=indent + "  ")


def groupby_loc(locs):
    X = defaultdict(list)
    S = defaultdict(float)

    for loc in locs:
        key = tuple(sorted(x[0] for x in loc.ssid_strength()[:3]))
        strength = sum(x[1] for x in loc.ssid_strength()[:3])
        X[key].append(loc)
        S[key] += strength

    return sorted(((S[x], x) for x in X.keys()), reverse=1)

def tabulate(locs, k=3):
    # tabulate according to the top-k ssids
    # total physical locations
    # total signal
    # total segments
    # total readings

    result = []

    physicals = defaultdict(list)
    signals = defaultdict(float)
    nsegments = defaultdict(int)
    nreadings = defaultdict(int)

    for loc in locs:
        key = tuple(sorted(x[0] for x in loc.ssid_strength()[:k]))
        physicals[key].append(loc)
        signals[key] += sum(x[1] for x in loc.ssid_strength()[:k])
        nsegments[key] += len(loc.clusters)
        nreadings[key] += sum(len(C.readings()) for C in loc.clusters)

    for key in physicals.keys():
        locs = physicals[key]
        sig = signals[key]
        seg = nsegments[key]
        rd  = nreadings[key]
        result.append((key, locs, sig, seg, rd))

    return result

def tuple_string(x):
    s = ""
    for i in range(3):
        v = x[i] if i < len(x) else ""
        s += "%30s" % v
    return s

def merge(tab, keys, lookup):
    K = set(keys)
    A = filter(lambda row: K.issubset(set(row[0])), tab)
    r = [keys, [], 0, 0, 0]
    for row in A:
        lookup[row[0]] = tuple(sorted(keys))
        for i,v in enumerate(row):
            if i > 0:
                r[i] += v

    B = list(filter(lambda row: not K.issubset(set(row[0])), tab))
    B.insert(0, tuple(r))
    return B

def Kolmogorov(tab, keys):
    K = set(keys)
    return len(list(r for r in tab if K.issubset(set(r[0]))))

def all_pairs(tab):
    for row in tab:
        S = list(row[0])
        for i in range(len(S)):
            x = S[i]
            for j in range(i+1, len(S)):
                y = S[j]
                yield (x,y)

def all_ones(tab):
    for row in tab:
        for k in row[0]:
            yield (k,)

def opt_key(tab, all_keys):
    key0 = None
    w0 = 0
    for i, key in enumerate(all_keys):
        w = Kolmogorov(tab, key)
        if i == 0 or w > w0:
            key0, w0 = key, w
    return (key0, w0)

#
# genfun is either all_ones or all_pairs
#
def reduce_tab(tab, genfun):
    all_keys = genfun(tab)

    key, w0 = opt_key(tab, all_keys)

    lookup = dict()

    while w0 > 1:
        print("......... merge %s .........." % str(key))
        tab = merge(tab, key, lookup)
        all_keys = genfun(tab)
        key, w0 = opt_key(tab, all_keys)

    return tab, lookup

#
# Uses a maximal likelihood estimation
# to determine the location of a segment
# based on the tabular locations.
#
def resolve_location(seg, tab, topK=3):
    def rank_score(row, lookup):
        return sum(lookup.get(x, 0) for x in row[0])

    lookup = dict(seg.ssid_strength())
    row0 = None
    rank0 = None
    for row in tab:
        rank = rank_score(row, lookup)
        if row0 == None or rank0 < rank:
            row0, rank0 = row, rank

    return row0, rank0


def build_timeline(movements, tab, lookup, w_min):

    def locstr(loc):
        return "/".join(sorted(loc))

    #  Builds timeline
    all_L = set()
    timeline = []
    for i,seg in enumerate(movements):
        row, w = resolve_location(seg, tab)
        loc = lookup.get(row[0], row[0])

        if w < w_min:
            continue

        t0, t1, dt = seg.timespan()

        timeline.append(dict(
            index=i,
            location=locstr(loc),
            strength=w,
            t0=t0,
            t1=t1,
            dt=dt))

        all_L.add(locstr(loc))

    return all_L, timeline


def save_timeline(filename, message, movements, tab, lookup, w_min):

    all_L, timeline = build_timeline(movements, tab, lookup, w_min)

    # make the data a dict for now, but will switch to list later
    data = {}
    for l in all_L:
        data[l] = { "location": l, "segments": []}

    # store each segment of time in its corresponding location
    for i in range(0, len(timeline)-1):
        data[timeline[i]["location"]]["segments"].append({"start": timeline[i]["t0"][0:10]+"T"+timeline[i]["t0"][11:16],
                                                          "end": timeline[i]["t1"][0:10]+"T"+timeline[i]["t1"][11:16]})

    # make json friendly location/segments
    location_json = []
    for key, value in data.items():
        location_json.append(value)

    #print(json.dumps(location_json, sort_keys=True, indent=4, separators=(',', ': ')))

    with open(filename, "w") as f:
        json.dump(location_json, f)

    print("DONE:", message)


def save_transitions(filename, message, movements, tab, lookup, w_min):

    all_L, timeline = build_timeline(movements, tab, lookup, w_min)

    # generate a dictionary of locations that have a unique ID
    # and a storage for summing up time spent there
    locations = {}
    location_id = 0
    for l in all_L:
        locations[l] = {"id": location_id,
                         "name": l,
                         "total_time": 0}
        location_id += 1

    # Make a 2D table of all the possible locations, and store how many times that transition
    # has been taken (might as well since we can)
    transitions = [[0 for x in range(len(locations))] for x in range(len(locations))]   # [from][to] value is the count
    for i in range(0, len(timeline)-2):
        transitions[locations[timeline[i]["location"]]["id"]][locations[timeline[i+1]["location"]]["id"]] += 1
        locations[timeline[i]["location"]]["total_time"] += timeline[i]["dt"] # sums up the total time spent

    # Since we skip the last one in the previous for loop we need to grab the location total time fo the last one
    locations[timeline[len(timeline)-1]["location"]]["total_time"] += timeline[len(timeline)-1]["dt"]

    # make json friendly location
    location_json = []
    for key, value in locations.items():
        location_json.append(value)

    transition_json = []
    #  make json friendly transition data
    for i in range(0, len(transitions)-1):
        for j in range(0, len(transitions)-1):
            if transitions[i][j] > 0:
                transition_json.append({"source": i, "target": j, "value": transitions[i][j]})

    data = {"locations": location_json,
            "transitions": transition_json}

    with open(filename, "w") as f:
        json.dump(data, f)

    print("DONE:", message)
        

if __name__ == '__main__':
    random.seed(0)
    (H, movements, locs) = pre_analyze(sys.argv[1])

    def strength(loc):
        return sum(x[1] for x in loc.ssid_strength()[:3])

    locs = sorted(locs, key=strength, reverse=1)

    # Group-by to L0
    tab0 = tabulate(locs)

    # Localization to L1
    tab1, lookup1 = reduce_tab(tab0, all_pairs)

    # Localization to L2
    tab2, lookup2 = reduce_tab(tab0, all_ones)

    # Write the timelines out
    save_timeline("L0_timeline.json",
            "L0 timeline",
            movements,
            tab0,
            dict(),
            0)

    save_transitions("L0.json",
            "L0 unfiltered",
            movements,
            tab0,
            dict(),
            0)

    save_timeline("L0_filtered_timeline.json",
            "L0 filtered timeline",
            movements,
            tab0,
            dict(),
            5)

    save_transitions("L0_filtered.json",
            "L0 filtered",
            movements,
            tab0,
            dict(),
            5)

    save_timeline("L1_timeline.json",
            "L1 timeline",
            movements,
            tab1,
            lookup1,
            0)

    save_transitions("L1.json",
            "L1 unfiltered",
            movements,
            tab1,
            lookup1,
            0)

    save_timeline("L1_filtered_timeline.json",
            "L0 timeline",
            movements,
            tab1,
            lookup1,
            5)

    save_transitions("L1_filtered.json",
            "L1 filtered",
            movements,
            tab1,
            lookup1,
            5)

    save_timeline("L2_timeline.json",
            "L2 timeline",
            movements,
            tab2,
            lookup2,
            0)

    save_transitions("L2.json",
            "L2 unfiltered",
            movements,
            tab2,
            lookup2,
            0)

    save_timeline("L2_filtered_timeline.json",
            "L2 filtered timeline",
            movements,
            tab2,
            lookup2,
            5)

    save_transitions("L2_filtered.json",
            "L2 filtered",
            movements,
            tab2,
            lookup2,
            5)

