import sys, os
import sqlite3
import itertools

DB = os.environ.get("MOBILE_DB")

if not DB:
    raise Exception("MOBILE_DB not set")

def connect():
    return sqlite3.connect(DB)

def stream_raw_samples():
    db = connect()
    sql = """
        SELECT stamp, bssid, strength 
        FROM scan
        ORDER BY stamp ASC
    """
    c = db.cursor()
    c.execute(sql)
    colnames = [x[0] for x in c.description]
    while True:
        try:
            row = c.fetchone()
            yield dict(zip(colnames, row))
            if not row:
                break
        except:
            break
    
    db.close()


def stream_readings():
    for stamp, readings in itertools.groupby(
            stream_raw_samples(),
            key=lambda x: x["stamp"]):
        readings = [x for x in readings if x["bssid"] and not x["strength"] == 0]
        yield dict(stamp=stamp, readings=readings)


def reading_similarity(x, y):
    r1, r2 = x["readings"], y["readings"]
    n1, n2 = len(r1), len(r2)

    if min(n1, n2) == 0 and n1+n2 > 0:
        return 0

    if n1 == 0 and n2 == 0:
        return None

    common = dict()
    n = 0
    for r in r1:
        common[r["bssid"]] = 1
    for r in r2:
        if r["bssid"] in common:
            n += 1

    return float(n) / max(n1, n2)

def slide_window(stream, k):
    window = [None for i in range(k)]

    for i, x in enumerate(stream):
        window[0:k-1] = window[1:k]
        window[k-1] = x
        if i >= k-1:
            yield list(window)
