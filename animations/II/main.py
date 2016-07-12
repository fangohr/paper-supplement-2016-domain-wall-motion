import os
import numpy as np
from fidimag.atomistic import Sim, UniformExchange, Anisotropy
from fidimag.common import CuboidMesh
import fidimag.common.constant as const


mu0 = 4 * np.pi * 1e-7
global_V = 1e-27
global_mu_s = 1/mu0*global_V
global_J = 2e-20
global_D = 0.01*global_J

global_mesh = CuboidMesh(nx=1, ny=1, nz=8000,
                  dx=1.0, dy=1.0, dz=1.0,
                  unit_length=1e-9)

def init_m(pos):

    z = pos[2]

    if z < 600:
        return (0, 0, 1)
    elif 600 <= z < 700:
        return (1, 1, 0)
    else:
        return (0, 0, -1)


def relax_system():

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


def excite_system(beta=0.0, jz=6, p=0.7, name='dyn'):

    # Specify the stt dynamics in the simulation
    sim = Sim(global_mesh, name=name, driver='llg_stt')

    sim.set_tols(rtol=1e-10, atol=1e-12)
    sim.alpha = 0.015
    sim.gamma = const.gamma
    sim.mu_s = global_mu_s

    # sim.set_m(init_m)
    sim.set_m(np.load('../m0.npy'))

    exch = UniformExchange(global_J)
    sim.add(exch)

    anis = Anisotropy(global_D, axis=(0,0,1))
    sim.add(anis)

    # Set the current in the z direction, in A / m
    # beta is the parameter in the STT torque
    sim.jz = -1.0e12*jz
    sim.beta = beta
    sim.p = p

    # The simulation will run for 2 ns and save
    # 100 snapshots of the system in the process
    ts = np.linspace(0, 2e-9, 101)

    for t in ts:
        print 'time', t
        sim.run_until(t)
        #sim.save_vtk()
        sim.save_m()


def do_sim(beta, u, P=0.7):

    u0 = const.g_e * const.mu_B* P*global_V / (2 * const.c_e*global_mu_s) #u=u0*je

    je = u/u0*1e-12
    
    path = os.getcwd()

    folder_name = 'beta_%g_u_%g' %(beta, u)
    if not os.path.exists(folder_name):
        os.makedirs(folder_name) 

    os.chdir(folder_name)

    excite_system(beta=beta,jz=je)

    os.chdir(path)

if __name__ == '__main__':

    relax_system()
    
    do_sim(beta=0.05, u=400)
    do_sim(beta=0.1, u=500)

