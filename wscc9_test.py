import andes
import matplotlib.pyplot as plt

ss = andes.run('wscc9_dyn.xlsx')
ss.TDS.config.tf = 5
ss.TDS.run()
ss.TDS.plot(ss.GENCLS.omega)
plt.show()