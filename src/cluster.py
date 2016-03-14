import random
import time
from collections import defaultdict

IDCounter = 0

class Cluster(object):
    children    = None
    parent      = None

    __bssid_cache__ = None
    __readings_cache__ = None

    def __init__(self, parent, *children):
        global IDCounter
        self.parent   = parent
        self.children = list(children)
        self.id       = IDCounter
        IDCounter     += 1

        for c in children:
            if isinstance(c, Cluster):
                c.parent = self

    def is_leaf(self):
        return len(self.children) < 2

    def is_root(self):
        return self.parent == None

    def left(self, *new_left):
        if len(new_left) > 0:
            C = new_left[0]
            C.parent = self
            self.children[0] = C
            self.nullify_cache()

        return self.children[0]

    def right(self, *new_right):
        if len(new_right) > 0:
            C = new_right[0]
            C.parent = self
            self.children[1] = C
            self.nullify_cache()

        return self.children[1]

    def rightmost(self):
        if self.is_leaf():
            return self
        else:
            return self.right().rightmost()

    def bssids(self):
        if self.__bssid_cache__:
            return self.__bssid_cache__

        result = None
        if self.is_leaf():
            reading = self.children[0]
            result  = reading.bssids.keys()
        else:
            result = self.left().bssids() | self.right().bssids()

        self.__bssid_cache__ = result
        return result 

    def leaves(self):
        if self.__readings_cache__:
            return self.__readings_cache__

        result = None
        if self.is_leaf():
            result = [self]
        else:
            result = self.left().leaves() + self.right().leaves()
        self.__readings_cache__ = result

        return result

    def readings(self):
        return [C.children[0] for C in self.leaves()]

    def ssid_strength(self):
        result = defaultdict(float)

        for r in self.readings():
            for x in r.bssids.values():
                result[x["ssid"]] += normalize_strength(x["strength"])

        ssids = sorted(result.keys(), key=lambda x: result[x], reverse=1)
        return [(x, result[x]) for x in ssids]

    def timespan(C):
        readings = C.readings()
        if len(readings) == 0:
            return None
        else:
            first, last = readings[0].stamp, readings[-1].stamp
            t0 = time.mktime(time.strptime(first, "%Y-%m-%d %H:%M:%S"))
            t1 = time.mktime(time.strptime(last, "%Y-%m-%d %H:%M:%S"))
            return (first, last, t1 - t0)


    def minsim(self, leaves=None):
        if leaves == None:
            leaves = self.leaves()

        min_s = 1
        for i in range(len(leaves)):
            Ci = leaves[i]
            for j in range(i, len(leaves)):
                Cj = leaves[j]
                s = sim(Ci, Cj)
                min_s = min(s, min_s)
        return min_s

    def stochastic_minsim(self, k=100):
        leaves = self.leaves()
        leaves = random.sample(leaves, k) if len(leaves) > k else leaves
        return self.minsim(leaves)

    def nullify_cache(self):
        self.__bssid_cache__ = None
        self.__readings_cache = None
        if self.parent:
            self.parent.nullify_cache()

class Hierarchy(object):
    root = None
    def __init__(self, first_reading):
        self.root = Cluster(None, first_reading)

    def append(self, r_new):
        C_insert = self.root.rightmost()
        C_new = Cluster(None, r_new)
        self.insert(C_insert, C_new)

    def insert(self, C_insert, C_new):
        if C_insert.is_root():
            self.root = Cluster(None, C_insert, C_new)
        else:
            parent = C_insert.parent
            C_prev = parent.left()
            assert parent.right() == C_insert

            if sim(C_insert, C_new) <= sim(C_prev, C_insert):
                # new point is too far
                self.insert(parent, C_new)
            else:
                # new point is close, so the sibling 
                # (C_prev, C_insert)
                # needs to be broken up
                C_tmp = Cluster(None, C_insert, C_new)
                if parent.is_root():
                    parent.right(C_tmp)
                else:
                    grdparent = parent.parent
                    grdparent.right(C_prev)
                    self.insert(C_prev.rightmost(), C_tmp)

    def print(self, C=None, indent=""):
        if C == None:
            C = self.root
        print("%s[%2d]: %d BSSIDs" % (indent, C.id, len(C.bssids())))
        if not C.is_leaf():
            self.print(C.left(), indent + "  ")
            self.print(C.right(), indent + "  ")

        if not indent:
            print("=" * 40)

class Location(object):

    def __init__(self, C):
        self.clusters = [C]

    def accept(self, C_new, threshold):
        for C in self.clusters:
            if sim(C, C_new) > threshold:
                self.clusters.append(C_new)
                return True
        return False

    def total_duration(self):
        total = 0
        for C in self.clusters:
            try:
                t0, t1, dt = C.timespan()
                total += dt
            except:
                pass
        return total

    def ssid_strength(self):
        result = defaultdict(int)

        for C in self.clusters:
            for ssid, strength in C.ssid_strength():
                result[ssid] += strength

        ssids = sorted(result.keys(), key=lambda x: result[x], reverse=1)
        return [(x, result[x]) for x in ssids]

def sim(C1, C2):
    A, B = C1.bssids(), C2.bssids()
    return float(len(A & B)) / len(A | B)

def segment(C, threshold=0.5, k=100):
    if isinstance(C, Hierarchy):
        return segment(C.root, threshold)
    if C.stochastic_minsim(k) >= threshold:
        return [C]
    else:
        A = segment(C.left(), threshold, k) 
        B = segment(C.right(), threshold, k)
        return A + B

def locations(tops, threshold=0.1):
    "Group the segments together as long as their threshold is good."
    locs = []
    for i,C in enumerate(tops):
        if i == 0:
            locs.append(Location(C))
        else:
            accepted = False
            for L in locs:
                if L.accept(C, threshold):
                    accepted = True
                    break
            if not accepted:
                locs.append(Location(C))

    return sorted(locs, key=lambda L: len(L.clusters), reverse=1)

def normalize_strength(dB):
    if dB <= -100: dB = -100
    if dB >= 0: dB = 0
    return dB/100.0 + 1;
