import mobile
import cluster
import itertools
import time
import sys

if sys.argv[1:]:
    mobile.DB = sys.argv[1]
else:
    print("Usage: %s <db>" % sys.argv[0])
    sys.exit()


index_start = 0
index_finish = 4000

with open("cluster_time.json", "w") as outfile:
    outfile.writelines("[ ")

with open("segmentation_time.json", "w") as outfile:
    outfile.writelines("[ ")

with open("location_time.json", "w") as outfile:
    outfile.writelines("[ ")


for total_readings in range(index_start, index_finish):

    readings = mobile.stream_readings()

    # Clustering
    start = time.time()
    H = cluster.Hierarchy(next(readings))
    for i, r in enumerate(readings):
        if i == total_readings:
            break
        H.append(r)

    with open("cluster_time.json", "a") as myfile:
        myfile.writelines("{ \"readings\":%d, \"time\":%.2f }" % (total_readings, (time.time() - start)))
        if total_readings < index_finish:
            myfile.writelines(", ")


    # Segmentation
    start = time.time()
    tops = cluster.segment(H, threshold=0.01)
    with open("segmentation_time.json", "a") as myfile:
        myfile.writelines("{ \"readings\":%d, \"time\":%.2f }" % (total_readings, (time.time() - start)))
        if total_readings < index_finish:
            myfile.writelines(", ")

    # Locations
    start = time.time()
    locs = cluster.locations(tops, threshold=0.1)
    with open("location_time.json", "a") as myfile:
        myfile.writelines("{ \"readings\":%d, \"time\":%.2f }" % (total_readings, (time.time() - start)))
        if total_readings < index_finish:
            myfile.writelines(", ")


with open("cluster_time.json", "a") as myfile:
    myfile.writelines("]")

with open("segmentation_time.json", "a") as myfile:
    myfile.writelines("]")

with open("location_time.json", "a") as myfile:
    myfile.writelines("]")
