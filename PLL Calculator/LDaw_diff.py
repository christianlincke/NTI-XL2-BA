"""
Plot L_DAW und Reduktion
nicht in der BA genutzt!

C. Lincke, April 2026
"""
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot

l_diff = np.empty(shape=(13,185))
for i in range(13):
    l_daw_off = np.loadtxt(f"plls_relative/hv_{i + 1:02}_off_.txt")
    l_daw_on = np.loadtxt(f"plls_relative/hv_{i+1:02}_on_.txt")
    l_diff[i] = -l_daw_off - -l_daw_on # negative db values, hence -l_xxx
    #plt.plot(l_diff[i], label=f"{i+1}")

# calculate mean by intensity
linear = 10 ** (l_diff * 0.1)
linear_mean = np.mean(linear, axis=0)
mean_int = 10 * np.log10(linear_mean)

# calculate mean by levels
mean_level = np.mean(l_diff, axis=0)
sd_level = np.std(l_diff, axis=0)

# make twin x plot
host = host_subplot(111)
par = host.twinx()

host.set_xlabel("t [mm:ss]")
host.set_xlim([15,185])
host.set_ylabel(r"$\overline{\Delta L}_{DAW}$ [dB]")
host.set_ylim([-8, 0])

par.set_ylabel("$S_{L_{DAW}}$ [dB]")
par.set_ylim([0,6])
# plot
p1, = host.plot(mean_level, label=r"$\overline{\Delta L}_{DAW}$ [dB]")
p2, = par.plot(sd_level, label="$S_{L_{DAW}}$", linewidth=1, linestyle="--")

host.legend(labelcolor="linecolor")

host.yaxis.label.set_color(p1.get_color())
par.yaxis.label.set_color(p2.get_color())

plt.grid()
plt.show()




