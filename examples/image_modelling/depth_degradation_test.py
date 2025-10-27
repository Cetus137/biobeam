import numpy as np
import tifffile as tiff
from gputools import perlin3
from biobeam import SimLSM_Lattice , SimLSM_Cylindrical
import matplotlib.pyplot as plt

def create_dn(size_um , dims , dn_amplitude , noise_amplitude, noise_scale=30):
   
    """Create a refractive index difference volume with given dimensions and noise amplitude."""
    size_um = (size_um, size_um, size_um) 
    N = dims
    dx = size_um[0] / N
    x = dx * (np.arange(N) - N//2)
    Z, Y, X = np.meshgrid(x, x, x, indexing="ij")

    noise = noise_amplitude * perlin3((N, N, N), scale=noise_scale)
    background = dn_amplitude * np.ones((N,N,N ))

    dn = noise + background
    
    return dn

def prepare_2D_fluorescence_sample(path):
    """Load a 2D fluorescent sample from a TIFF file."""
    print("\nCreating fluorescent sample...")
    img = tiff.imread(path)
    print(f"  Sample loaded from {path} with shape {img.shape}")

    img_volume = np.zeros((img.shape[0], img.shape[1], img.shape[1]))
    for i in range(img_volume.shape[0]):
        img_volume[:, :, i] = img


    '''
    # Duplicate 2D image along z to form a (Z, Y, X) volume
    if img.ndim == 2:
        z = img.shape[0]
        img = np.repeat(img[None, :, :], repeats=z, axis=0)
        print(f"  Duplicated to volume with shape {img.shape}")
    
    plt.imshow(img[0,:,:])
    plt.show()

    # Rotate 90 degrees around the Y axis (swap Z and X)
    img = np.rot90(img, k=1, axes=(0,2))
    print(img.shape)

    plt.imshow(img[:,:,0])
    plt.show()
    '''
    img = img_volume
  
    tiff.imwrite("fluorescent_sample_volume.tiff", img.astype(np.float32))
    
    return img


if __name__ == "__main__":

    #Load fluorescent sample
    path = r'/Users/edwheeler/Desktop/rotation2/CARE_test_frames/clean/frame_0001_depth_25.tif'
    print("\nCreating fluorescent sample...")
    img = prepare_2D_fluorescence_sample(path)
    print(f"  Sample loaded from {path} with shape {img.shape}")

    # Parameters
    size_um = 30  # Physical size of the volume in microns
    dims = img.shape[0]     # Number of voxels along each dimension
    dn_amplitude = 0.2  # Amplitude of refractive index variations

    print("\nCreating tissue model...")
    dn = create_dn(size_um, dims, dn_amplitude, noise_amplitude=0.00)
    print(f"  Tissue: Perlin noise with amplitude {dn_amplitude}")
    #plt.imshow(dn[dims//2], cmap='gray')
    #plt.title('Refractive Index Difference Slice (dn)')
    #plt.colorbar(label='dn value')
    #plt.show()


    print("\nSimulating Images")
    m = SimLSM_Cylindrical( dn=dn,
                        signal = img,
                        size = (dims,dims,dims),
                        lam_illum=0.488,
                        #NA_illum2=0.40,
                        #NA_illum1=0.35,
                        NA_detect=0.6,
                        n0=1.33,
    )

    # Get just the illumination (no sample)
    illumination = m.propagate_illum(cz=0)

    # Look at a slice
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 4))
    plt.subplot(121)
    plt.imshow(illumination[illumination.shape[0]//2, :, :].T, cmap='hot')
    plt.title('Light sheet XY view')
    plt.xlabel('X (propagation)')
    plt.ylabel('Y')

    plt.subplot(122)
    plt.imshow(illumination[:, illumination.shape[1]//2, :].T, cmap='hot')
    plt.title('Light sheet XZ view')
    plt.xlabel('X (propagation)')
    plt.ylabel('Z (detection)')
    plt.show()

    image = m.simulate_image_z(cz = -20)
    tiff.imwrite("depth_degraded_image.tiff", image.astype(np.float32))
    print("  Simulated image saved to depth_degraded_image.tiff")

