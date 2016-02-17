__author__ = 'adele'


import mobile

class SampleVector:

    def __init__(self, *children):
        self.children = children
        self.__cached_bssids__ = None
        self.sim_to_next = None            # Each group will contain the similarity to the NEXT group

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
                self.hierarchy[i].sim_to_next = sim
                if sim > sim_max:
                    i_max, sim_max = i, sim


            # Merge groups with consecutive max similarity
            i = 0
            start_index = None
            end_index = None
            while i < len(self.hierarchy):

                # if we found a sim max
                if self.hierarchy[i].sim_to_next == sim_max:

                    # If the start/end hasn't been set, then initialize it
                    # and so long as we are within a set of the max sim then
                    # keep moving the end_index over
                    if start_index is None:
                        start_index = i
                        end_index = i+1
                    else:
                        end_index = i+1

                # if we found the max sim in the past, but the current sim doesnt match
                # then group what we have found and restart start_index and end_index
                elif self.hierarchy[i].sim_to_next != sim_max and start_index is not None:
                    self.merge_range(start_index, end_index)
                    print "merged [%d to %d], %d left" % (start_index, end_index, len(self.hierarchy))
                    i = i - (end_index - start_index)
                    start_index = None
                    end_index = None

                i += 1


            return i_max, sim_max
        else:
            return None

    def build_hierarchy(self):
        iter = 0
        while len(self.hierarchy) > 1:
            (imax, smax) = self.merge_pass()
            iter += 1
            print "######################################\n[SWEEP %d] - %d left" % (iter, len(self.hierarchy))

