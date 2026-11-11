import andes
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# SETUP
#ss = andes.load('wscc9_dyn.xlsx')

# SETUP
ss = andes.load(andes.get_case('wscc9/wscc9.xlsx'), setup=False)
andes.config_logger(stream_level=20)

ss.add('GENCLS', dict(idx='G1', bus=1, gen=1, Sn=100, M=21.0, D=0, xd1=0.0608,  ra=0))
#GENERATOR 2: Base = 100MVA, M = 12.08, xd = 0.1198
ss.add('REGCA1', dict(idx='G2', bus=2, gen=2, Sn=100, xs=0.1198, ra=0))
#ss.add('GENCLS', dict(idx='G2', bus=2, gen=2, Sn=100, M=9.82, D=0, xd1=0.1198,  ra=0))
#GENERATOR 1: Base = 100MVA, M = 6.08, xd = 0.1813
ss.add('GENCLS', dict(idx='G3', bus=3, gen=3, Sn=100, M=7.20,  D=0, xd1=0.1813, ra=0))


    # Add a Toggle to trip GENROU_2 at t=1 second
gen_indxs = list(ss.GENCLS.idx.v)   # list of each index for each generator
ren_indxs = list(ss.REGCA1.idx.v)
#ss.add("Toggle", model="GENCLS", dev=gen_indxs[1], t=1.0)   # trips generator 1 at time 1.0 s

ss.setup()
andes.io.xlsx.write(ss, 'Jasmine_wscc9_dyn.xlsx', overwrite=True)

"""
# User input, to change inertia constant per generator
ss.GENCLS.M.v[0] = 7.0  # 1 simple cycle gas turbine --> if it is 3, would the inertia constant be 21?
# ss.GENCLS.M.v[1] = 0.0  # solar yard
ss.GENCLS.M.v[1] = 7.2  # HVDC grid forming converter
"""

# TODO:
# show inertia at each generator over a time period (40 sec?)
# show rocof over that time period as well

# display each generation curve
# display each load curve

# change generation values - secondary objective
# change load values - secondary objective

# NEXT STEPS: 
#   show inertia at each BUS over a period of time (build bus frequency file from ANDES documentation)


# Run a time domain simulation
ss.PFlow.run()
ss.TDS.config.tf = 8
ss.TDS.config.no_tqdm = 1
ss.TDS.config.criteria = 0
ss.TDS.run()

print("inertia vals: ", ss.GENCLS.M.v)
print("syngen indicies: ", gen_indxs)   # prints G1, G3
print("reneweable gen indices: ", ren_indxs)    # prints G2

# plotting frequency over time
ss.TDS.load_plotter()


fig, ax = ss.TDS.plt.plot(
    ss.GENCLS.omega,
    a=(0, 1),  # Plots first 3 buses (generator buses)
    ytimes=60,  # convert from per-unit frequency to Hz for a 60 Hz system
    ylabel='Frequency [Hz]'
)

"""
fig, cx = ss.TDS.plt.plot(
    ss.REGCA1.v,
)


fig, bx = ss.TDS.plt.plot(
    ss.Bus.v,
    ylabel='Bus Voltage [per-unit]',
    show=False         # don't display yet ---------- Claude.ai
)

# Replace the default legend with a positioned one
bx.legend(
    loc='center left',
    bbox_to_anchor=(1.01, 0.5),   # just outside the right edge of the axes
    ncol=1,
    fontsize=8,
    frameon=False,
)


fig.tight_layout()
plt.show()      # ----------------------------------------- end Claude.ai
"""

fig, dx = ss.TDS.plt.plot(
    ss.GENCLS.M,
    a=(0,1)
)




