import mobile
from cluster import *
from itertools import *

R = list(islice(mobile.stream_readings(), 0, 150))

C1 = Cluster(None, Cluster(None, R[0]), Cluster(None, R[1]))
C2 = Cluster(None, R[-1])

print("Sim = %.4f" % sim(C1, C2))
