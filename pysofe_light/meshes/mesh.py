"""
Provides the data structure for approximating the spatial domain
of the partial differential equation.
"""

# IMPORTS
import numpy as np

import refinements
from .geometry import MeshGeometry
from .topology import MeshTopology
from .reference_map import ReferenceMap

class Mesh(object):
    """
    Provides a class for general meshes.

    Basically clues together the MeshGeometry and MeshTopology
    classes and provides interfaces for mesh refinement and
    global point search.

    Parameters
    ----------

    nodes : array_like
        The coordinates of the mesh nodes

    connectivity : array_like
        The connectivity array defining the mesh cells via their vertex indices
    """

    def __init__(self, nodes, connectivity):
        # transform input arguments if neccessary
        nodes = np.atleast_2d(nodes)
        connectivity = np.asarray(connectivity, dtype=int)

        # check input arguments
        assert 1 <= nodes.shape[1] <= 3
        
        # get mesh dimension from nodes
        self._dimension = nodes.shape[1]

        # init mesh geometry and topology
        self.geometry = MeshGeometry(nodes)
        self.topology = MeshTopology(cells=connectivity, dimension=self._dimension)

        # init reference maps class
        self.ref_map = ReferenceMap(self)

    @property
    def dimension(self):
        """
        The spatial dimension fo the mesh.
        """
        return self._dimension

    @property
    def nodes(self):
        """
        The coordinates of the mesh nodes.
        """
        return self.geometry.nodes

    @property
    def cells(self):
        """
        The incident vertex indices of the mesh cells.
        """
        # the mesh cells have the same topological dimension as the mesh dimension
        return self.topology.get_entities(d=self.dimension)

    @property
    def facets(self):
        """
        The incident vertex indices of the mesh facets.
        """
        # the mesh facets have topological codimension 1
        return self.topology.get_entities(d=self.dimension - 1)

    @property
    def faces(self):
        """
        The incident vertex indices of the mesh faces.
        """
        # faces are mesh entities of topological dimension 2
        return self.topology.get_entities(d=2)

    @property
    def edges(self):
        """
        The incident vertex indices of the mesh edges.
        """
        # edges are mesh entities of topological dimension 1
        return self.topology.get_entities(d=1)

    def boundary(self, fnc=None):
        """
        Determines the mesh facets that are part of the boundary specified
        by the function `fnc` and returns a corresponding boolean array.

        Parameters
        ----------

        fnc : callable
            Function specifying some part of the boundary for which
            to return the corresponding facets
        """

        # get a mask specifying the boundary facets
        boundary_mask = self.topology.get_boundary(d=self.dimension-1)

        if fnc is not None:
            assert callable(fnc)

            # to determine the facets that belong to the desired
            # part of the boundary we compute the centroids of
            # all boundary facets and pass them as arguments to
            # the given function which shall return True for all
            # those that belong to the specified part

            # to compute the centroids we need the vertex indices of
            # every facet and the corresponding node coordinates
            facet_vertices = self.facets.compress(boundary_mask, axis=0)
            facet_vertex_coordinates = self.nodes.take(facet_vertices - 1, axis=0)
            centroids = facet_vertex_coordinates.mean(axis=1)

            # pass them to the given function (column-wise)
            try:
                part_mask = fnc(centroids.T)
            except:
                # given function might not be vectorized
                # so try looping over the centroids
                # --> may be slow
                ncentroids = np.size(centroids, axis=0)
                part_mask = np.empty(shape=(ncentroids,), dtype=bool)

                for i in xrange(ncentroids):
                    part_mask[i] = fnc(centroids[i,:])

            boundary_mask[boundary_mask] = np.logical_and(boundary_mask[boundary_mask], part_mask)

        return boundary_mask

    def refine(self, method='uniform', **kwargs):
        """
        Refines the mesh using the given method.

        Parameters
        ----------

        method : str
            A string specifying the refinement method to use
        """
        refinements.refine(mesh=self, method=method, inplace=True, **kwargs)

    def eval_function(self, fnc, points):
        """
        Evaluates a given function in the global mesh points corresponding
        to the given local points on the reference domain.

        Parameters
        ----------

        fnc : callable
            The function to evaluate

        points : array_like
            The local points on the reference domain
        """
        raise NotImplementedError()
    

