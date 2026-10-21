#Testing 123
import andes
import matplotlib.pyplot as plt

ss = andes.run(andes.get_case('kundur/kundur_full.xlsx'))
ss.TDS.config.tf = 10
ss.TDS.run()
ss.TDS.plot(ss.GENROU.omega)
plt.show()
