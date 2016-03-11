import random

IDCounter = 0

class Cluster(object):
    children = None
    parent   = None

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

    def hetero(self, leaves=None):
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

    def stochastic_hetero(self, k=100):
        leaves = self.leaves()
        leaves = random.sample(leaves, k) if len(leaves) > k else leaves
        return self.hetero(leaves)

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

def sim(C1, C2):
    A, B = C1.bssids(), C2.bssids()
    return float(len(A & B)) / len(A | B)

