import andes
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

#ss = andes.load(andes.get_case('wscc9/wscc9.raw'))
ss = andes.load('wscc9_dyn.xlsx')

print("number buses: ", ss.Bus.idx.n)
ss.PFlow.run()
ss.Bus.v.v

#ss.GENCLS.M.v[0] = 8.0


# ---------------------------------------------------- #
"""
ss.TDS.config.tf = 10
ss.TDS.run()
#ss.TDS.plot(ss.GENCLS.omega)
#plt.show()

#print(ss.GENCLS.doc())

print("PV generators:", ss.PV.n)
print("Slack generators:", ss.Slack.n)
print("GENCLS machines:", ss.GENCLS.n)
print("GENROU machines:", ss.GENROU.n)
"""
# get generator data
#print("\nSynchronous generator data:")
#print(ss.SynGen.as_df())



print("inertia vals: ", ss.GENCLS.M.v)
# Get inertia from each generator bus - from ANDES website documentation
gen_indxs = list(ss.GENCLS.idx.v)   # list of each index for each generator
gen_buses = list(ss.GENCLS.bus.v)
M_base = ss.GENCLS.M.v.copy()
print("M base: ", M_base)

gen_info = pd.DataFrame({"gen_indx": gen_indxs, "bus": gen_buses, "M": M_base})
gen_info.sort_values("M", ascending=False)

print("generator information:")
print(gen_info)

# from ANDES website example documentation
trip_idx = gen_indxs[int(np.argmax(M_base))]

inertia_scales = [1.0, 0.7, 0.5, 0.4, 0.3, 0.2, 0.15]
#inertia_scales = [0.15, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0]
results = {} 


for alpha in inertia_scales:
    ss = andes.load('wscc9_dyn.xlsx', setup=False) 
    ss.add("Toggle", model="GENCLS", dev=trip_idx, t=1.0)       # trips generator with highest inertia 
    ss.setup()
    ss.config.warn_abnormal = 0
    ss.GENCLS.M.v[:] = M_base * alpha

    ss.PFlow.run()
    ss.TDS.config.tf = 8
    ss.TDS.config.no_tqdm = 1
    ss.TDS.config.criteria = 0
    ss.TDS.run()

    results[alpha] = ss.TDS.get_timeseries(ss.GENCLS.omega)



weights = M_base / M_base.sum()
cmap = plt.cm.RdYlBu

fig, ax = plt.subplots(figsize=(6, 4))

for i, (alpha, omega_df) in enumerate(results.items()):
    f_coi = (omega_df.values * weights).sum(axis=1) * 60
    color = cmap(i / (len(results) - 1))
    ax.plot(omega_df.index, f_coi, color=color, linewidth=1.8,
            label=f"$\\alpha$ = {alpha}")

ax.set_xlabel("Time [s]")
ax.set_ylabel("COI frequency [Hz]")
ax.set_title("WSCC 9: frequency response after generator trip")
ax.legend(loc="lower right", fontsize=9, framealpha=0.9)
ax.set_xlim(0.5, 5.0)
ax.axhline(60.0, color="black", linewidth=0.4, alpha=0.3)

plt.tight_layout()
plt.show()
    





