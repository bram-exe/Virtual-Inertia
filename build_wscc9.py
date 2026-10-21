import andes, os
cases = os.path.dirname(os.path.dirname(andes.get_case('kundur/kundur_full.xlsx')))
#print(sorted(os.listdir(cases)))
#print(os.listdir(os.path.join(cases, 'ieee9')) if 'ieee9' in os.listdir(cases) else "no ieee9 folder")

#print(os.listdir(os.path.join(cases, 'wscc9')))

ss = andes.load(andes.get_case('wscc9/wscc9.xlsx'), setup=False)
#print(ss.GENROU.as_df())
#print(ss.GENCLS.as_df())
#print(ss.Toggle.as_df())
# no generators present in the file, so its mainly a power flow model

#print(ss.PV.as_df()[['idx', 'bus', 'Sn', 'p0']])
#print(ss.Slack.as_df()[['idx', 'bus', 'Sn', 'p0']])

ss = andes.load(andes.get_case('wscc9/wscc9.xlsx'), setup=False)

#-----------------------------Documentation-----------------------------
#adding genertion: 
#Format: 
#idx: Name for generator
#bus: bus the generator connects to
#gen: generator (PV or slack) this model connects to [idx]
#Sn: Machine power rating [MVA]
#M: Inertial constant, M = 2H [seconds]
#D: Damping coefficient [pu]
#xd1: d axis transient reactance, think of an internal resistance between generators internal voltage and terminals 
#       ^^Affects how generators swign against each other and how power redistributes after a a disturbance^^
#ra: internal resistance of motor stator. 

#Using numbers from https://arxiv.org/pdf/2405.11427 <- just a test for now, come back and cite later
#------------------------------------------------------------------------

#GENERATOR 1: Base = 100MVA, M = 47.28, xd = 0.0608
ss.add('GENCLS', dict(idx='G1', bus=1, gen=1, Sn=100, M=47.28, D=0, xd1=0.0608,  ra=0))
#GENERATOR 2: Base = 100MVA, M = 12.08, xd = 0.1198
ss.add('GENCLS', dict(idx='G2', bus=2, gen=2, Sn=100, M=12.08,  D=0, xd1=0.1198, ra=0))
#GENERATOR 1: Base = 100MVA, M = 6.08, xd = 0.1813
ss.add('GENCLS', dict(idx='G3', bus=3, gen=3, Sn=100, M=6.02,  D=0, xd1=0.1813, ra=0))

ss.setup()
andes.io.xlsx.write(ss, 'wscc9_dyn.xlsx', overwrite=True)