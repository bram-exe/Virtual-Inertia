"""
    Attempting to build a 9 bus system in this file. 
    Generator Bus 1: Natural Gas turbine (Slack Bus)
    Generator Bus 2: Solar Yard (Grid following, no inertia)
    Generator Bus 3: HVDC with GFM inverter ###COME BACK TO WITH A REALISTIC M VALUE) 

    Load 5: Utility (Use values from WSCC)
    Load 6: Utility (Use values from WSCC)
    Load 7: Data center (New PQ Load)
    Load 8: WSCC Load????
    Change to fort collins load^^^
"""
import andes 
import numpy as np
import matplotlib.pyplot as plt
import argparse

# Using 100MVA system base 

DEFAULTS = dict(
    G1_Sn = 250, G1_H = 5.0, #Gas turbine 
    M_vsm = 4.0, #Virtual inertia from GFM HVDC
    D_vsm = 0.0, kw_vsm=20.0, #damping and droop
    dc_P = 1.0, dc_Q = 0.20 #Data center load info in per unit
)

#Tuning dict for grid forming inverter
REGCV1_GAINS = dict(
    kv = 0.0, #Voltage droop/ reactive Power vs voltage 
    xs = 0.1, #reactance between converter and grid
    Tc = 0.01, #10ms lag 
    Kpvd = 15.0,
    Kivd = 1.0, 
    Kpvq = 15.0,
    Kivq = 1.0, 
    KpId = 1.0,
    KiId = 1.0, 
    KpIq = 1.0,
    KiIq = 1.0,
)

Load = dict(

)


def build(out='9bus_sim_bram.xlsx', **overrides):
    p = {**DEFAULTS, **overrides}
    ss = andes.load(andes.get_case('wscc9/wscc9.xlsx'), setup=False, no_output=True)

    #-------------------------Generator 1-------------------------
    ss.Slack.Sn.v[0] = p['G1_Sn']
    ss.add('GENROU', dict(idx = 'G1_gas', 
                          bus = 1, 
                          gen = 1, 
                          Sn = p['G1_Sn'], 
                          Vn = 16.5, # kV Voltage base -> must match bus
                          M = 2 * p["G1_H"], # M = 2H
                          D = 0, 
                          ra = 0, # negligable stator resistance
                          xl = 0.15, # leakage [p.u.]
                          xd = 1.8, # d-axis reactance [p.u.]
                          xq = 1.7, # q-axis reactance [p.u.]
                          xd1 = 0.3, # transient reacatance (1 meaning ')
                          xq1 = 0.55, # transient reacatance
                          xd2 = 0.25, # subtransient reactance (2 meaning '')
                          xq2 = 0.25, # subtransient reactance
                          Td10 = 8.0, # How transient/subtransiet effects decay
                          Tq10 = 0.4,
                          Td20 = 0.03, 
                          Tq20 = 0.05,
                          ))
    ss.add('TGOV1', dict(idx = "GOV_G1", 
                         syn = 'G1_gas',
                         R = 0.05, # 5% droop in freq causes full power increase
                         VMAX = 1.2, #pu limit
                         VMIN = 0.0,
                         T1 = 0.5, #Time constants for how turbine responds
                         T2 = 3.0,
                         T3 = 10.0, 
                         Dt = 0, # Turbine damping off
                         ))
    ss.add('SEXS', dict(idx = 'EXC_G1', syn = 'G1_gas'))

    #-------------------------Generator 2-------------------------
    #WECC Modeling chain technique:

    #REPCA1 plant controller controls plant level V/Q/Freq <come back 
    #                        v
    #REECA1 for electrical controls decides what P and Q to produce, current limits
    #                        v
    #REGCA1 for inverterthat injects into bus 

    #_________________________________________________________________come back to add REPCA1 for a plant controller later
    ss.add('REGCA1', dict(idx='G2_solar', bus=2, gen=2, Sn=250))

    #ANDES Needs these 5 defined
    ss.add('REECA1', dict(idx='REE_G2', 
                          reg='G2_solar',
                          PFFLAG=0, # Hold constant Q, set to =1 to hold constant PF
                          VFLAG=0,  # voltage control in Q loop (ignored since QFLAG=0)
                          QFLAG=0, # bypass Q/V control loops
                          PFLAG=0, # P command not scaled by frequency
                          PQFLAG=0, # Q priority when current-limited
                          ))

    #-------------------------Generator 3-------------------------
    ss.add('REGCV1', dict(idx='G3_gfm', 
                          bus = 3, 
                          gen = 3, 
                          Sn = 100,
                          M = p['M_vsm'], 
                          D = p['D_vsm'], 
                          kw = p['kw_vsm'], 
                          **REGCV1_GAINS))

    #-------------------------Data Center Load-------------------------
    ss.add('PQ', dict(idx='DC_7', 
                      name='DataCenter', 
                      bus=7,
                     p0=p['dc_P'], 
                      q0=p['dc_Q']))

    #ss.add("PQ", dict(idx='Load Profile'




    #))

    ss.setup()
    andes.io.xlsx.write(ss, out, overwrite=True)
    return out

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='9bus_sim_bram.xlsx')
    for k, v in DEFAULTS.items():
        ap.add_argument(f'--{k}', type=float, default=v)
    a = vars(ap.parse_args())
    #print('wrote', build(a.pop('out'), **a))
    out = build(a.pop('out'), **a)
    print('wrote', out)
    # --- sanity check: 10 s with NO disturbance, frequency should stay at 60 Hz ---
    #ss = andes.load(out, no_output=True)
    #ss.PFlow.run()
    #ss.TDS.config.tf = 10
    #ss.TDS.run()
    #f = ss.dae.ts.x[:, ss.GENROU.omega.a[0]] * 60
    #print(f'gas unit freq: min {f.min():.4f} Hz, max {f.max():.4f} Hz')

    #print(ss.PQ.as_df())
    # --- trip scenario: switch one device off at t = 1 s ---
    """
    TRIP_MODEL, TRIP_DEV, T_TRIP, TF = 'PQ', 'DC_7', 1.0, 20.0

    ss = andes.load(out, setup=False, no_output=True)   # setup=False so we can add the Toggle
    ss.add('Toggle', dict(model=TRIP_MODEL, dev=TRIP_DEV, t=T_TRIP))
    ss.setup()
    ss.PFlow.run()
    ss.TDS.config.tf = TF
    ss.TDS.config.criteria = 0
    ss.TDS.run()

    t   = np.array(ss.dae.ts.t)
    f_g = ss.dae.ts.x[:, ss.GENROU.omega.a[0]] * 60
    f_v = ss.dae.ts.y[:, ss.REGCV1.omega.a[0]] * 60
    i0, i1 = np.searchsorted(t, T_TRIP), np.searchsorted(t, T_TRIP + 0.5)
    print(f'{TRIP_DEV} trip: peak {f_g.max():.3f} Hz | nadir {f_g.min():.3f} Hz | '
          f'RoCoF {(f_g[i1]-f_g[i0])/(t[i1]-t[i0]):+.3f} Hz/s | final {f_g[-1]:.3f} Hz')

    plt.plot(t, f_g, label='Gas unit (G1)')
    plt.plot(t, f_v, '--', label='GFM inverter (G3)')
    plt.axhline(60, color='k', lw=0.4)
    plt.xlabel('Time [s]'); plt.ylabel('Frequency [Hz]')
    plt.title(f'{TRIP_DEV} trip at t = {T_TRIP} s')
    plt.legend(); plt.show()

    #Create visualizer 
    

    #Load profiles??? 
     #Research for load profiles
       #Creating an interface for the model -> 
         #argparse()
    #Researching proper values for test case

    #Build a test/trip scenario
        #Look into ANDES Gen trip scenario to modify for a load
        #Node with weak inertia -> dispatch inertia -> correct it. 

    # How can you crossreference a class between pythn files
    # get_time.py 
"""
def run_trip(M, trip_model='PQ', trip_dev='DC_7', t_trip=1.0, tf=20.0, **overrides):
    """Build a case with virtual inertia M, trip one device at t_trip, return the results."""
    out = build(f'trip_M{M}.xlsx', M_vsm=M, **overrides)
    ss = andes.load(out, setup=False, no_output=True)
    ss.add('Toggle', dict(model=trip_model, dev=trip_dev, t=t_trip))   # the trip event
    ss.setup()
    ss.PFlow.run()
    ss.TDS.config.tf = tf
    ss.TDS.config.criteria = 0      # don't stop early if angles swing apart
    ss.TDS.config.no_tqdm = 1       # hide the progress bar
    ss.TDS.run()

    t = np.array(ss.dae.ts.t)
    f = ss.dae.ts.x[:, ss.GENROU.omega.a[0]] * 60          # gas unit freq [Hz] (state -> ts.x)
    f_v = ss.dae.ts.y[:, ss.REGCV1.omega.a[0]] * 60        # GFM inverter freq [Hz] (algebraic -> ts.y)
    i0, i1 = np.searchsorted(t, t_trip), np.searchsorted(t, t_trip + 0.5)
    return dict(M=M, t=t, f=f, f_v=f_v,
                peak=f.max(), nadir=f.min(),
                rocof=(f[i1] - f[i0]) / (t[i1] - t[i0]),  # over first 0.5 s after trip
                final=f[-1], t_end=t[-1])


if __name__ == '__main__':
    
    TRIP_MODEL, TRIP_DEV = 'PQ', 'DC_7'     # what trips 
    M_LIST = [0.5, 1, 2, 4, 8, 16, 32]      # virtual inertia 
    ROCOF_LIMIT = 1.0                       # Hz/s PLACEHOLDER

    out = build('9bus_sim_bram.xlsx')
    print('wrote', out)
    ss = andes.load(out, no_output=True)
    ss.PFlow.run()
    ss.TDS.config.tf = 10
    ss.TDS.config.no_tqdm = 1
    ss.TDS.run()
    f = ss.dae.ts.x[:, ss.GENROU.omega.a[0]] * 60
    print(f'sanity check (no disturbance): {f.min():.4f} to {f.max():.4f} Hz  -> should be 60.0000')

    results = []
    for M in M_LIST:
        print(f'running M = {M} s ...')
        results.append(run_trip(M, TRIP_MODEL, TRIP_DEV))

    print(f"\n{TRIP_DEV} trip at t = 1 s")
    print(f"{'M [s]':>6} {'H [s]':>6} {'MW*s':>7} {'peak [Hz]':>10} {'nadir [Hz]':>11} {'RoCoF [Hz/s]':>13} {'final [Hz]':>11}")
    for r in results:
        H = r['M'] / 2
        print(f"{r['M']:>6} {H:>6} {H*100:>7.0f} {r['peak']:>10.3f} {r['nadir']:>11.3f} "
              f"{r['rocof']:>13.3f} {r['final']:>11.3f}")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
    cmap = plt.cm.viridis
    for i, r in enumerate(results):
        ax1.plot(r['t'], r['f'], color=cmap(i / (len(results) - 1)), label=f"M = {r['M']} s")
    ax1.axhline(60, color='k', lw=0.4)
    ax1.set_xlabel('Time [s]'); ax1.set_ylabel('Gas unit frequency [Hz]')
    ax1.set_title(f'{TRIP_DEV} trip: frequency response')
    ax1.legend(fontsize=8)

    Ms = [r['M'] for r in results]
    ax2.plot(Ms, [abs(r['rocof']) for r in results], 'o-')
    ax2.axhline(ROCOF_LIMIT, color='r', ls='--', label=f'RoCoF limit ({ROCOF_LIMIT} Hz/s, placeholder)')
    ax2.set_xscale('log')
    ax2.set_xlabel('Virtual inertia M [s]'); ax2.set_ylabel('|RoCoF| [Hz/s]')
    ax2.set_title('RoCoF vs virtual inertia')
    ax2.legend()

    plt.tight_layout()
    plt.savefig('trip_sweep.png', dpi=150)
    plt.show()
