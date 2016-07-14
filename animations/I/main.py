import numpy as np
from fidimag.atomistic import Sim, UniformExchange, Anisotropy
from fidimag.common import CuboidMesh
import fidimag.common.constant as const

# Here we define physical constants:
mu0 = 4 * np.pi * 1e-7
global_V = 1e-27
global_mu_s = 1/mu0*global_V
global_J = 2e-20
global_D = 0.01*global_J

# Here we create the cuboid mesh, where on each node a spin
# is placed. Note that the chain is 1-D.

global_mesh = CuboidMesh(nx=1, ny=1, nz=4000,
                  dx=1.0, dy=1.0, dz=1.0,
                  unit_length=1e-9)

def init_m(pos):
    """
    This function initialises an approximate domain wall in the z direction.
    """
    z = pos[2]

    if z < 1200:
        return (0, 0, 1)
    elif 1200 <= z < 1400:
        return (1, 1, 0)
    else:
        return (0, 0, -1)


def relax_system():
    """
    This function creates a simulation object, and relaxes the system,
    saving the magnetisation after the relaxation.
    """
    # Only relaxation
    sim = Sim(global_mesh, name='relax')

    # Simulation parameters
    sim.set_tols(rtol=1e-8, atol=1e-10)
    sim.alpha = 0.5
    sim.gamma = const.gamma
    sim.mu_s = global_mu_s
    sim.do_precession = False

    # The initial state passed as a function
    sim.set_m(init_m)

    exch = UniformExchange(global_J)
    sim.add(exch)

    anis = Anisotropy(global_D, axis=(0,0,1))
    sim.add(anis)

    sim.relax(dt=1e-14, stopping_dmdt=1e5, max_steps=5000,
              save_m_steps=None, save_vtk_steps=None)

    np.save('m0.npy', sim.spin)


def current_function_1(t):
    """
    This function returns the value of a sinusoidal current at a given simulation 
    time t. 0 <= j <= 1.
    """    
    return (1-np.cos(1e9*t*np.pi/2.0))/2.0

def current_function_2(t):
    """
    This function returns the value of a square wave current at a given simulation 
    time t. 0 <= j <= 1.
    """
    t1 = t*1e9%2.0
    if t1<1.0:
        return 0
    else:
        return 1.0


def excite_system(beta=0.0, jz=6, p=0.7, current_function=None, name='dynamic'):
    # In this function, we load the magnetisation from the relaxation,
    # and apply a current.
    # Specify the spin transfer torque (STT)  dynamics in the simulation
    sim = Sim(global_mesh, name=name, driver='llg_stt')

    sim.set_tols(rtol=1e-10, atol=1e-12)
    sim.alpha = 0.015
    sim.gamma = const.gamma
    sim.mu_s = global_mu_s
    # Here we set the magnetisation equal to that from the relaxed system.    
    sim.set_m(np.load('m0.npy'))

    # Here we add energy terms to the simulation:
    exch = UniformExchange(global_J)
    sim.add(exch)
    anis = Anisotropy(global_D, axis=(0,0,1))
    sim.add(anis)

    # Set the current in the z direction, in A / m
    # beta is the parameter in the STT torque
    sim.jz = -1.0e12*jz
    sim.beta = beta
    sim.p = p
    sim.update_j_fun = current_function

    # The simulation will run for 6 nanoseconds and save
    # 301 snapshots of the system in the process
    ts = np.linspace(0, 6e-9, 301)

    for t in ts:
        print 'time', t
        sim.run_until(t)
        # sim.save_vtk() # Uncomment this line to save VTK files of the magnetisation.
        sim.save_m()


def do_sim(u=300, beta=0.03, P = 0.7):

    u0 = const.g_e * const.mu_B* P*global_V / (2 * const.c_e*global_mu_s) #u=u0*je

    je = u/u0*1e-12

    print('je=', je)

    excite_system(beta=beta, jz=je, current_function=current_function_1, name='sinusoidal_current')
    excite_system(beta=beta, jz=je, current_function=current_function_2, name='square_wave_current')


if __name__ == '__main__':

    # Relax the initial state

    relax_system()
    do_sim(u=300,beta=0.03)
    
 


