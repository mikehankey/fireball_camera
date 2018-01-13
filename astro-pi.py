import matplotlib.pyplot as plt
import os
from astropy.io import fits
from astropy.wcs import WCS
from astropy import units as u
image_file = "/var/www/html/out/cal/good/20180105232017-1-sd.new"

hdu = fits.open(image_file)
hdu.info()

wcs = WCS(hdu[0].header)

fig = plt.figure()

ax = fig.add_axes([0.0,0.0,.8,.8],projection=wcs)
ax.set_xlim(-0.1, hdu[0].data.shape[1] - 0.1)
ax.set_ylim(-0.1, hdu[0].data.shape[0] - 0.1)

ax.imshow(hdu[0].data, origin='lower')

overlay = ax.get_coords_overlay('fk5')

overlay['ra'].set_ticks(color='white', number=8)
overlay['dec'].set_ticks(color='white', number=8)

overlay['ra'].set_axislabel('Right Ascension')
overlay['dec'].set_axislabel('Declination')

overlay.grid(color='white', linestyle='dashed', alpha=0.5)

plt.savefig("test.png")
os.system("convert test.png -flip testf.png")
#plt.show()
