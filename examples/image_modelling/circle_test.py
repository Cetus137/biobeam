import numpy as np
from biobeam import SimLSM_Cylindrical
#from biobeam.data import tiling
from gputools import perlin3
import tifffile as tiff

def create_dn_and_signal_sphere( N, path):
    """ generates a re fra ct iv e i n h o m o g e n e o u s
    sphere and an image as given by the
    function tiling () """

    img = tiff.imread(path)
    x = np . linspace ( -50 ,50 , N )
    Xs = np . meshgrid (x ,x ,x , indexing = "ij" )
    R = np . sqrt (np.sum ([ _X **2 for _X in Xs ] , axis = 0))
    # generate the r efr ac tiv e index d i f f e r e n c e s
    dn = (0.02 +0.00 * perlin3(( N ,N , N ) , scale =3))  * ( R < 35)

    signal = np.einsum( "i , kj" , np.ones ( N ) , img)
    img_volume = np.zeros((img.shape[0], img.shape[1], img.shape[1]))
    for i in range(img_volume.shape[0]):
        img_volume[:, :, i] = img
    
    signal = img_volume
    tiff.imwrite("fluorescent_signal_volume.tiff", signal.astype(np.float32))
    return dn , signal

def create_dn_and_signal(N , path , dn_amplitude , noise_amplitude, noise_scale=30):
    img = tiff.imread(path)
    x = np . linspace ( -50 ,50 , N )
    Xs = np . meshgrid (x ,x ,x , indexing = "ij" )

    dn = noise_amplitude * perlin3(( N ,N , N ) , scale = noise_scale) + dn_amplitude * np.ones((N,N,N ))
    tiff.imwrite("refractive_index_difference_volume.tiff", dn.astype(np.float32))
    img_volume = np.zeros((img.shape[0], img.shape[1], img.shape[1]))
    for i in range(img_volume.shape[0]):
        img_volume[:, :, i] = img
    signal = img_volume
    tiff.imwrite("fluorescent_signal_volume.tiff", signal.astype(np.float32))
    return dn , signal




if __name__ == "__main__":
    path = r'/Users/edwheeler/Desktop/rotation2/CARE_test_frames/clean/frame_0001_depth_25.tif'
    # create re fra ct iv e i n h o m o g e n e o u s
    # sphere and an image as given by the
    # function tiling ( )
    N = 256
    dn , signal = create_dn_and_signal(N = N, path = path, dn_amplitude = 0.2 , noise_amplitude=0.05, noise_scale=30)
    # create a m ic ros co pe simulator
    m = SimLSM_Cylindrical(dn = dn , signal = signal ,NA_illum =.1 , NA_detect =.45 , size = ( N,N ,N) , n0 =1.33)
    # generate image as recorded by the microscope
    # at an axial position -20 um relative to center
    idx = 0
    for cz in range(-N//2 + 1, N//2 - 1 , 1):
        print(cz)
        image = m.simulate_image_z( cz = cz , psf_grid_dim=(16 ,16) , conv_sub_blocks=(2 ,2), zslice=1)[0]
        tiff.imwrite("./outputs/cylindrical_depth_degradation_image_cz_" + str(idx) + ".tiff", image.astype(np.float32))
        idx +=1