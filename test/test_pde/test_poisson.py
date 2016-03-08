"""
Tests the Poisson equation.
"""

import numpy as np
import pysofe_light as pysofe

# create neccessary setup

# 1D case
nodes_1d = np.array([[0.],[1.]])
cells_1d = np.array([[1, 2]])
mesh_1d = pysofe.meshes.mesh.Mesh(nodes_1d, cells_1d)
mesh_1d.refine(method='uniform', times=5)

element_1d = pysofe.elements.simple.lagrange.P1(dimension=1)

fes_1d = pysofe.spaces.space.FESpace(mesh_1d, element_1d)

class TestPoisson1D(object):
    def dir_domain(x):
        dir0 = np.logical_or(x[0] == 0., x[0] == 1.)
        return dir0

    dir_bc = pysofe.pde.conditions.DirichletBC(fe_space=fes_1d,
                                               domain=dir_domain,
                                               ud=1.)

    pde = pysofe.pde.poisson.Poisson(fe_space=fes_1d, a=1., f=0., bc=dir_bc)

    def test_solution(self):
        sol = self.pde.solve()

        assert np.allclose(sol, np.ones(self.pde.fe_space.n_dof))

# 2D case
nodes_2d = np.array([[0.,0.],[1.,0.],[0.,1.],[1.,1.]])
cells_2d = np.array([[1, 2, 3], [2, 3, 4]])
mesh_2d = pysofe.meshes.mesh.Mesh(nodes_2d, cells_2d)
mesh_2d.refine(method='uniform', times=4)

element_2d = pysofe.elements.simple.lagrange.P1(dimension=2)

fes_2d = pysofe.spaces.space.FESpace(mesh_2d, element_2d)

class TestPoisson2D(object):
    def dir_domain(x):
        dir0 = np.logical_or(x[0] == 0., x[0] == 1.)
        dir1 = np.logical_or(x[1] == 0., x[1] == 1.)
        return np.logical_or(dir0, dir1)

    dir_bc = pysofe.pde.conditions.DirichletBC(fe_space=fes_2d,
                                               domain=dir_domain,
                                               ud=1.)

    pde = pysofe.pde.poisson.Poisson(fe_space=fes_2d, a=1., f=0., bc=dir_bc)

    def test_solution(self):
        sol = self.pde.solve()

        assert np.allclose(sol, np.ones(self.pde.fe_space.n_dof))
