import sys, os
import sqlite3
import itertools
import traceback

DB = os.environ.get("MOBILE_DB")

class Reading(object):
    stamp = None
    bssids = None
    def __init__(self, stamp, raw_readings):
        self.stamp = stamp
        self.bssids = dict(
                (x["bssid"], dict(ssid=x["ssid"], strength=x["strength"])
                    ) for x in raw_readings)

    def __str__(self):
        return "[%s]{%s}" % (self.stamp, ";".join(self.ssids()))

    def ssids(self):
        return sorted(x["ssid"] for x in self.bssids.values())



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
            if not row:
                break

            row = list(row)
            if row[0] and row[1] and row[2]:
                row[1] = row[1].upper()
                yield dict(zip(colnames, row))
        except Exception as e:
            traceback.print_exc()
            sys.exit()
            break
    
    db.close()


def stream_readings():
    for stamp, raw_readings in itertools.groupby(
            stream_raw_readings(),
            key=lambda x: x["stamp"]):
        yield Reading(stamp, raw_readings)


def slide_window(stream, k):
    window = [None for i in range(k)]

    for i, x in enumerate(stream):
        window[0:k-1] = window[1:k]
        window[k-1] = x
        if i >= k-1:
            yield list(window)


