import mobile
from cluster import *
from itertools import *
import json

IDCounter = 0

def set_readings_total(node):

    if hasattr(node, "total"):
        return node.total

    if hasattr(node, "children"):
        if len(node.children) == 1:
            node.total = 1
            return 1

        else:
            node.total = set_readings_total(node.children[0]) + set_readings_total(node.children[1])
            return node.total

    return 1


def get_node(node):
    global IDCounter
    d = {}
    d["name"] = IDCounter
    d["similarity"] = 1.0 #this will get overwritten if there are 2 children
    d["total"] = set_readings_total(node)
    IDCounter += 1

    if hasattr(node, "children"):
        left_child = get_node(node.children[0])
        d["children"] = [left_child]

        if len(node.children) > 1:
            right_child = get_node(node.children[1])
            d["children"].append(right_child)
            d["similarity"] = sim(node.children[0], node.children[1])
            if len(right_child["children"]) > 1:
                d["end"] = right_child["end"]
            else:
                d["end"] = right_child["start"]

        d["start"] = left_child["start"]
    else:
        d["start"] = node.stamp[0:10]+"T"+node.stamp[11:16]
        d["children"] = []

    return d





n = 200

R = list(islice(mobile.stream_readings(), 0, n))

H = Hierarchy(R[0])

for r in islice(R, 1, n):
    H.append(r)

root = get_node(H.root)

print(json.dumps(root, indent=4))

with open("src/json/hierarchy.json", "w") as outfile:
    json.dump(root, outfile)




