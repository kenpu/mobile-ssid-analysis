import mobile
import cluster
import itertools
import time
import sys
from collections import defaultdict

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
        result.append((key, len(locs), sig, seg, rd))

    return result

def tuple_string(x):
    s = ""
    for i in range(3):
        v = x[i] if i < len(x) else ""
        s += "%30s" % v
    return s

if __name__ == '__main__':

    (H, movements, locs) = pre_analyze(sys.argv[1])

    def strength(loc):
        return sum(x[1] for x in loc.ssid_strength()[:3])

    locs = sorted(locs, key=strength, reverse=1)

    # Group-by
    tab = tabulate(locs)
    def print_row(row):
        print("%80s %5d %5.1f %5d %5d" % row)

    # Hack
    def merge(tab, keys):
        K = set(keys)
        A = filter(lambda row: keys.issubset(set(row[0])), tab)
        r = [keys, 0, 0, 0, 0]
        for row in A:
            for i,v in enumerate(row):
                if i > 0:
                    r[i] += v

        B = list(filter(lambda row: not keys.issubset(set(row[0])), tab))
        B.insert(0, tuple(r))
        return B

    if False:
        tab = merge(tab, set(["CAMPUS-AIR"]))
        tab = merge(tab, set(["DDSB-GUEST"]))
        tab = sorted(tab, key=lambda x: x[2], reverse=1)

        for x in tab:
            print_row(x)

    if True:
        # Compute the frequency of pairs
        pairs = defaultdict(float)
        for row in tab:
            for i,x in enumerate(row[0]):
                for j in range(i+1, len(row[0])):
                    y = row[0][j]
                    pairs[(x,y)] += row[2]
        for k in sorted(pairs.keys(), key=lambda x:pairs[x], reverse=1):
            print("%80s %.2f" % (k, pairs[k]))
