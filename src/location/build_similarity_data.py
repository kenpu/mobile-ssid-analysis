from mobile import *
import numpy as np
from jinja2 import Environment, FileSystemLoader
from algorithm_multi_merge import *
from time import time


tl = Timeline(stream_samples())

print len(tl.hierarchy)

if True:
    start = time()
    tl.sim_pass()
    duration = time() - start

    print "Completed similarity pass in %.2f seconds" % duration

    env = Environment(loader=FileSystemLoader('../template'))
    template = env.get_template('similarity_plot.html')

    y = [s.sim_to_next for s in tl.hierarchy]
    y = y[0:1000]
    x = range(0, len(y))

    # variables to be set
    scale_x_min = np.min(x)
    scale_x_max = np.max(x)
    scale_y_min = np.min(y)
    scale_y_max = np.max(y)
    my_list = np.column_stack((y, x))
    my_plot = template.render(scale_x_min=scale_x_min, scale_x_max=scale_x_max,
                              scale_y_min=scale_y_min, scale_y_max=scale_y_max,
                              my_list=my_list)
    #print my_plot
    with open("../rendered/similarity_plot.html", "wb") as fh:
        fh.write(my_plot)

    print("finished")






