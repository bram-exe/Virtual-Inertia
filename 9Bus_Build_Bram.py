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
import argparse

# Using 100MVA system base 

DEFAULTS = dict(
    G1_Sn = 250, G1_H = 5.0, #Gas turbine 
    M_vsm = 4.0, #Virtual inertia from GFM
    D_vsm = 0.0, kw_vsm=20.0, #damping and droop
    dc_P = 1.0, dc_Q = 0.20 #Data center load info in per unit
)

#Tuning dict for grid forming inverter
REGCV1_GAINS = dict(
    kv = 0.0, #Voltage droop/ reactive Power vs voltage 
    xs = 0.1, #reactance between converter and grid
    Tc = 0.01, #10ms lag 
    Kpvd = 5.0,
    Kivd = 0.1, 
    Kpvq = 5.0,
    Kivq = 0.1, 
    KpId = 0.05,
    KiId=0.1, 
    KpIq = 0.05,
    KiIq = 0.1,
)

def build(out='9bus_sim.xlsx', **overrides):
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

    #REPCA1 plant controller controls plant level V/Q/Freq
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

    ss.setup()
    andes.io.xlsx.write(ss, out, overwrite=True)
    return out

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='9bus_sim.xlsx')
    for k, v in DEFAULTS.items():
        ap.add_argument(f'--{k}', type=float, default=v)
    a = vars(ap.parse_args())
    #print('wrote', build(a.pop('out'), **a))
    out = build(a.pop('out'), **a)
    print('wrote', out)
    # --- sanity check: 10 s with NO disturbance, frequency should stay at 60 Hz ---
    ss = andes.load(out, no_output=True)
    ss.PFlow.run()
    ss.TDS.config.tf = 10
    ss.TDS.run()
    f = ss.dae.ts.x[:, ss.GENROU.omega.a[0]] * 60
    print(f'gas unit freq: min {f.min():.4f} Hz, max {f.max():.4f} Hz')