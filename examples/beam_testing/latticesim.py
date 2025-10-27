import numpy as np
from biobeam import SimLSM_Lattice

def create_dn ( N = 512):
    """ generates a refractive sphere """
    x = np.linspace( -50 ,50 , N )
    Xs = np.meshgrid(x ,x ,x , indexing = "ij" )
    R = np.sqrt ( np.sum([ _X **2 for _X in Xs ],axis = 0))
    # generate the r efr ac tiv e index d i f f e r e n c e s
    dn = .04*( R <20)
    return dn


dn = create_dn()
# create a m ic ros co pe simulator
m = SimLSM_Lattice( dn = dn  , size = (100 ,100 ,100) , n0 = 1.33)
# simulate the psf grid at an axial position
# -20 um relative to center
psfs = m.psf_grid_z(cz = -20 , grid_dim =(16 ,16) ,with_sheet = False)

print(psfs.shape)  # (z , y , x , n_y , n_x
print(psfs)