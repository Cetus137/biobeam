"""
generate_care_3d_light_sheet.py

Generates a 3D dithered Bessel lattice light sheet and propagates it
through a uniform tissue, producing a 3D clean + degraded volume.

Requirements:
- biobeam
- tifffile
- numpy
- bessel_lattice.py (your lattice generator)
"""

import numpy as np
import tifffile
import biobeam
from bessel_lattice import generate_bessel_lattice

# ----------------------
# Simulation parameters
# ----------------------
volume_shape = (128, 128, 128)  # (Z, Y, X)
voxel_size = 0.1                # microns
lam = 0.52                      # illumination wavelength in microns
NA_illum = 0.3                   # illumination NA
NA_det = 1.0                     # detection NA
lattice_centers = [(32,64), (64,64), (96,64)]
dither_fraction = 0.5
n_dither_steps = 5
n_samples = 1                   # number of volumes to generate

# ----------------------
# Loop over samples
# ----------------------
for i in range(n_samples):
    print(f"Generating 3D volume {i+1}/{n_samples}...")

    # 1. Generate clean lattice slice at Z=0
    clean_slice = generate_bessel_lattice(
        size_yx=(volume_shape[1], volume_shape[2]),
        lattice_centers=lattice_centers,
        NA_illum=NA_illum,
        dither_fraction=dither_fraction,
        n_dither_steps=n_dither_steps,
        save_path=None
    )

    # 2. Initialize uniform tissue (optional small variations)
    dn = np.zeros(volume_shape, dtype=np.float32)
    dn += 0.001 * np.random.normal(size=volume_shape)

    # 3. Initialize BPM model
    m = biobeam.Bpm3d(dn=dn, lam=lam, units=(voxel_size, voxel_size, voxel_size))

    # 4. Allocate 3D volumes
    clean_volume = np.zeros(volume_shape, dtype=np.float32)
    degraded_volume = np.zeros(volume_shape, dtype=np.float32)

    # 5. Propagate slice along Z
    for z in range(volume_shape[0]):
        # Propagate slice to depth z
        u = m.propagate(clean_slice, distance=z*voxel_size)
        # Store propagated intensity
        degraded_volume[z, :, :] = biobeam.apply_psf(np.abs(u)**2, m.psf(NA_det))
        # Clean volume can be the initial lattice repeated or scaled if desired
        clean_volume[z, :, :] = np.abs(clean_slice)**2

    # 6. Optional Poisson noise
    degraded_volume += np.random.poisson(lam=1, size=degraded_volume.shape).astype(np.float32)

    # 7. Save volumes
    tifffile.imwrite(f"clean_3d_{i:03d}.tif", clean_volume.astype(np.float32))
    tifffile.imwrite(f"degraded_3d_{i:03d}.tif", degraded_volume.astype(np.float32))

print("3D volumes generated successfully!")
