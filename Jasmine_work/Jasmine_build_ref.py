import andes 
import argparse
import build_bus_hold as build_bus 
import matplotlib.pyplot as plt
import numpy as np


# from Bram_build
# loads test case into ss
# writes DEFAULTS information into a
ap = argparse.ArgumentParser()
ap.add_argument('--out', default='9bus_sim.xlsx')
for k, v in build_bus.DEFAULTS.items():
    ap.add_argument(f'--{k}', type=float, default=v)
a = vars(ap.parse_args())   # a holds all values in DEFAULTS
#print('wrote', build(a.pop('out'), **a))
out = build_bus.build(a.pop('out'), **a)
print('wrote', out)
ss = andes.load(out, no_output=True)

ss.PFlow.run()
ss.TDS.config.tf = 10
ss.TDS.run()
#f = ss.TDS.get_timeseries(ss.GENROU.omega)
f = ss.dae.ts.x[:, ss.GENROU.omega.a[0]] * 60
print(f'gas unit freq: min {f.min():.4f} Hz, max {f.max():.4f} Hz')
fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(f)

#print(f'frequency time series: {f}')

# next: add inertia quantifier per generator bus for now
# include plot, value printing, perhaps have to solve for it in some cases

print('Inertia: ', ss.REGCV1.M.v)

# Print bus frequency
# H = (Pm - Pe)fs / (2 * ROCOF)     using swing equation
# https://ieeexplore.ieee.org/document/10977593 
frequencies = ss.TDS.get_timeseries(ss.BusFreq.f) * 60
print(f'bus frequencies: {frequencies.head()}')

plt.figure()
plt.plot(ss.dae.ts.t, frequencies)
plt.legend([f'Bus {bus}' for bus in ss.Bus.idx.v])
plt.show()





metrics = []
"""omega_df = ss.TDS.get_timeseries(ss.GENROU.omega)
print((omega_df.max(axis=0)) * 60)  # does the same thing as bram's code above, but is tied to the DEFAULTS item G1_gas

omega_df.append(ss.TDS.get_timeseries(ss.REGCV1.omega))

for k, v in build_bus.build(out):
    f_coi = (omega_df.values).sum(axis=1) * 60
    t = omega_df.index.values

    nadir = f_coi[t > 1.0].min()

    post = (t >= 1.0) & (t <= 2.0)
    t_post, f_post = t[post], f_coi[post]
    rocof = np.max(np.abs(np.diff(f_post) / np.diff(t_post)))

    metrics.append({"Nadir [Hz]": nadir, "RoCoF [Hz/s]": rocof})"""


