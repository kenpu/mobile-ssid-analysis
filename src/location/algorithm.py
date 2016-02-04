import mobile

class SampleVector:

    def __init__(self, *children):
        self.children = children
        self.__cached_bssids__ = None

    def bssids(self):
        if self.__cached_bssids__ is None:
            R = []
            for c in self.children:
                if isinstance(c, SampleVector):
                    R.extend(c.bssids())
                else:
                    R.extend(x["bssid"] for x in c["readings"])
            self.__cached_bssids__ = set(R)

        return self.__cached_bssids__


    def compare(self, another):
        x = self.bssids()
        y = another.bssids()

        return mobile.similarity(x, y)

class Timeline:

    def __init__(self, sample_stream):
        self.samples = list(sample_stream)
        self.hierarchy = [SampleVector(s) for s in self.samples]

    def merge_range(self, start, end):
        children = self.hierarchy[start : end+1]
        self.hierarchy[start : end+1] = [SampleVector(*children)]

    def merge_pass(self):
        n = len(self.hierarchy)
        if n > 1:
            i_max = 0
            sim_max = self.hierarchy[0].compare(self.hierarchy[1])

            for i in range(n-1):
                sim = self.hierarchy[i].compare(self.hierarchy[i+1])
                if sim > sim_max:
                    i_max, sim_max = i, sim

            self.merge_range(i_max, i_max+1)

            return i_max, sim_max
        else:
            return None

    def build_hierarchy(self):
        iter = 0
        while len(self.hierarchy) > 1:
            (imax, smax) = self.merge_pass()
            iter += 1
            print "[%d] at %d, %.2f, %d left" % (iter, imax, smax,
                    len(self.hierarchy))

