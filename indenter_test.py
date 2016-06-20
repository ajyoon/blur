#!/usr/bin/env python

import time

from . import prebuilt_networks
from .rand import weighted_option_rand, weighted_curve_rand

t_network = prebuilt_networks.indenter()

x = 25
t_network.pick()

count = 0
while count < 1000:
    out_string = ""
    for index in range(0, 200):
        out_string += " "
        if index == x:
            char_num = weighted_curve_rand([(6, 5,), (10, 30), (50, 4)])
            out_string += ('[' * char_num)
            break
    if count % 8 == 0:
        out_string = "-" + out_string[1:]
    x += t_network.current_node.get_value()
    if x < 0:
        x = 5
    if x > 200:
        x = 195

    print(out_string)
    t_network.pick()
    time.sleep(0.05)
    count += 1