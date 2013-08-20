__author__ = "Mikael Mortensen <mikaem@math.uio.no>"
__date__ = "2013-06-25"
__copyright__ = "Copyright (C) 2013 " + __author__
__license__  = "GNU Lesser GPL version 3 or any later version"

from Oasis import *

# Create a mesh here
mesh = RectangleMesh(0, 0, 2, 2, 20, 20)

# Override some problem specific parameters
NS_parameters.update(dict(
    nu = 0.01,
    T = 1,
    dt = 0.001,
    folder = "taylorgreen2D_results",
    max_iter = 3,
    iters_on_first_timestep = 2,
    convection = "Standard",
    use_krylov_solvers = False,
    use_lumping_of_mass_matrix = True,
    velocity_degree = 2,
    pressure_degree = 1,
    monitor_convergence = False,
    krylov_report = False    
  )
)

class PeriodicDomain(SubDomain):
    
    def inside(self, x, on_boundary):
        # return True if on left or bottom boundary AND NOT on one of the two corners (0, 1) and (1, 0)
        return bool((near(x[0], 0) or near(x[1], 0)) and 
              (not ((near(x[0], 0) and near(x[1], 2)) or 
                    (near(x[0], 2) and near(x[1], 0)))) and on_boundary)

    def map(self, x, y):
        if near(x[0], 2) and near(x[1], 2):
            y[0] = x[0] - 2.0
            y[1] = x[1] - 2.0
        elif near(x[0], 2):
            y[0] = x[0] - 2.0
            y[1] = x[1]
        else:
            y[0] = x[0]
            y[1] = x[1] - 2.0

constrained_domain = PeriodicDomain()

initial_fields = dict(
    u0='-sin(pi*x[1])*cos(pi*x[0])*exp(-2.*pi*pi*nu*t)',
    u1='sin(pi*x[0])*cos(pi*x[1])*exp(-2.*pi*pi*nu*t)',
    p='-(cos(2*pi*x[0])+cos(2*pi*x[1]))*exp(-4.*pi*pi*nu*t)/4.')
    
def initialize(q_, q_1, q_2, VV, t, nu, dt, **NS_namespace):
    for ui in q_.keys():
        deltat = dt/2. if ui is 'p' else 0.
        vv = project(Expression((initial_fields[ui]), t=t+deltat, nu=nu), VV[ui])
        q_[ui].vector()[:] = vv.vector()[:]
        if not ui == 'p':
            q_1[ui].vector()[:] = q_[ui].vector()[:]
            q_2[ui].vector()[:] = q_[ui].vector()[:]

def temporal_hook(q_, t, nu, VV, dt, **NS_namespace):
    plot(q_['u0'], title='u')
    plot(q_['u1'], title='v')
    plot(q_['p'], title='p')
    err = {}
    for ui in q_.keys():
        deltat = dt/2. if ui is 'p' else 0.
        vv = project(Expression((initial_fields[ui]), t=t-deltat, nu=nu), VV[ui])
        vv.vector().axpy(-1., q_[ui].vector())
        err[ui] = norm(vv.vector())
    print "Error at time = ", t, " is ", err
