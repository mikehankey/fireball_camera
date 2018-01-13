import fitsio 
import sys

filename = sys.argv[1] 
h = fitsio.read_header(filename, ext=1) 
n_entries = h["NAXIS2"] 
fits = fitsio.FITS(filename, iter_row_buffer=1000) 
print (fits)
print (h)
for i in range(n_entries): 
   print (fits[1][i])
   #entry = fits[1][i] 
   #print (entry)
