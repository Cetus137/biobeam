import numpy as np
import tifffile
import biobeam
from scipy.ndimage import shift

# Parameters
size_yx = (128, 128)
NA_illum = 0.3
lattice_centers = [(32, 64), (64, 64), (96, 64)]

# Dithering offsets (sub-pixel)
dither_offsets = [(0,0), (0.5,0), (-0.5,0), (0,0.5), (0,-0.5)]
N = len(dither_offsets)

# Initialize dithered lattice
dithered_lattice = np.zeros(size_yx, dtype=np.float32)

# Generate lattice and apply dithering
for dx, dy in dither_offsets:
    lattice = np.zeros(size_yx, dtype=np.complex64)
    for center in lattice_centers:
        lattice += biobeam.fields.make_bessel_field(size=size_yx, NA=NA_illum, center=center)
    # Apply subpixel shift
    lattice_shifted = shift(np.abs(lattice)**2, shift=(dy, dx), order=1, mode='nearest')
    dithered_lattice += lattice_shifted / N

# Save dithered lattice
tifffile.imwrite("bessel_lattice_dithered.tif", dithered_lattice.astype(np.float32))
print("Saved bessel_lattice_dithered.tif")
