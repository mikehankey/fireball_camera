import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

def skip_comments(f):
    '''
    Read lines that DO NOT start with a # symbol.
    '''
    for line in f:
        if not line.strip().startswith('#'):
            yield line

def get_data_bb():
    '''RA, DEC data file.
    '''

    # Path to data file.
    out_file = 'bb_cat.dat'

    # Read data file
    with open(out_file) as f:
        ra, dec = [], []

        for line in skip_comments(f):
            ra.append(float(line.split()[0]))
            dec.append(float(line.split()[1]))

    return ra, dec

# Read RA, DEC data from file.
ra, dec = get_data_bb()
# Convert RA from decimal degrees to radians.
ra = [x / 180.0 * 3.141593 for x in ra]

# Make plot.
fig = plt.figure(figsize=(20, 20))
gs = gridspec.GridSpec(4, 2)
# Position plot in figure using gridspec.
ax = plt.subplot(gs[0], polar=True)
ax.set_ylim(-90, -55)

# Set x,y ticks
angs = np.array([330., 345., 0., 15., 30., 45., 60., 75., 90., 105., 120.])
plt.xticks(angs * np.pi / 180., fontsize=8)
plt.yticks(np.arange(-80, -59, 10), fontsize=8)
ax.set_rlabel_position(120)
ax.set_xticklabels(['$22^h$', '$23^h$', '$0^h$', '$1^h$', '$2^h$', '$3^h$',
    '$4^h$', '$5^h$', '$6^h$', '$7^h$', '$8^h$'], fontsize=10)
ax.set_yticklabels(['$-80^{\circ}$', '$-70^{\circ}$', '$-60^{\circ}$'],
    fontsize=10)

# Plot points.
ax.scatter(ra, dec, marker='o', c='k', s=1, lw=0.)

# Use this block to generate colored points with a colorbar.
#cm = plt.cm.get_cmap('RdYlBu_r')
#z = np.random.random((len(ra), 1))  # RGB values
#SC = ax.scatter(ra, dec, marker='o', c=z, s=10, lw=0., cmap=cm)
# Colorbar
#cbar = plt.colorbar(SC, shrink=1., pad=0.05)
#cbar.ax.tick_params(labelsize=8)
#cbar.set_label('colorbar', fontsize=8)

# Output png file.
fig.tight_layout()
plt.savefig('ra_dec_plot.png', dpi=300)
