import sys, os
import sqlite3
import itertools

DB = os.environ.get("MOBILE_DB")

if not DB:
    raise Exception("MOBILE_DB not set")

def connect():
    return sqlite3.connect(DB)

def stream_raw_readings():
    db = connect()
    sql = """
        SELECT stamp, ssid, bssid, strength 
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


def stream_samples():
    for stamp, readings in itertools.groupby(
            stream_raw_readings(),
            key=lambda x: x["stamp"]):
        readings = [x for x in readings if x["bssid"] and not x["strength"] == 0]
        yield dict(stamp=stamp, readings=readings)


def sample_similarity(x, y):
    r1, r2 = set(x["readings"]), set(y["readings"])
    return similarity(r1, r2)

def slide_window(stream, k):
    window = [None for i in range(k)]

    for i, x in enumerate(stream):
        window[0:k-1] = window[1:k]
        window[k-1] = x
        if i >= k-1:
            yield list(window)

def similarity(x, y):
    n1, n2 = len(x), len(y)
    if min(n1, n2) == 0 and n1 + n2 > 0:
        return 0
    if n1 == 0 and n2 == 0:
        return None
    n = len(x.intersection(y))
    return float(n)/max(n1,n2)

