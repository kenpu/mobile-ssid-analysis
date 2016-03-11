import mobile
from itertools import *

for r in islice(mobile.stream_readings(), 0, 5):
    print(str(r))

