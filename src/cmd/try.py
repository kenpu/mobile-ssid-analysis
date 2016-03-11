import mobile
import cluster
import itertools
import time

readings = mobile.stream_readings()

start = time.time()

H = cluster.Hierarchy(next(readings))
for i, r in enumerate(readings):
    H.append(r)
    if i % 100 == 0:
        print(i)

print("Duration = %.2f seconds" % (time.time() - start))
H.print()

