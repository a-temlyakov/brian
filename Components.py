__author__ = """    Andrew Temlyakov (temlyaka@email.sc.edu)    """

from Population import *
from operator import itemgetter
import networkx as nx

class Components(object):
    def __init__(self, affinity_matrix=None):
        self.affinity_matrix = affinity_matrix
        self._connected_components = None
        self._component_affinity_matrix = None
        self._component_centers = None
        self._total_components = 1

    def print_self(self):
        print "Affinity Matrix: ", self.affinity_matrix
        print "Connected Components: ", self._connected_components
        print "Component Affinity Matrix: ", self._component_affinity_matrix
        print "Total Components: ", self._total_components
        print "Component Centers: ", self._component_centers
        
    def get_components(self, threshold, affinity_matrix=None):
        similarity_graph = nx.Graph()

        if affinity_matrix is None:
            distances = self.affinity_matrix
        else:
            distances = affinity_matrix
       
        num_instances = len(distances)

        similarity_graph.add_nodes_from(range(num_instances))

        #build the graph from upper triangular
        for i in range(num_instances):
            for j in range(i + 1, num_instances):
                if distances[i, j] <= threshold:
                    similarity_graph.add_edge(i, j, weight = distances[i, j])

        self._connected_components = \
                        nx.connected_components(similarity_graph)
        self._total_components = len(self._connected_components)
        self._component_affinity_matrix = \
                        self._get_component_difference(distances)
        return self._connected_components, self._component_affinity_matrix

    def _get_component_difference(self, distances):
        component_affinity_matrix = \
                    zeros((self._total_components, self._total_components))

        for i, temp_component in enumerate(self._connected_components):
            for j in range(i + 1, self._total_components):
                component_affinity_matrix[i, j] = \
                                     self.__component_diff(temp_component,
                                            self._connected_components[j],
                                            distances)

        component_affinity_matrix += component_affinity_matrix.transpose()
        return component_affinity_matrix

    def __component_diff(self, temp_component, targ_component, distances):
        score_sum = 0

        for temp_idx in temp_component:
            score_sum += mean(distances[temp_idx, targ_component])

        return score_sum / float(len(temp_component))

    def _expand_component_difference(self, affinity_matrix=None):
        if affinity_matrix is None:
            distances = self.affinity_matrix
        else:
            distances = affinity_matrix

        comp_matrix = zeros((len(distances), len(distances)))
        comp_sort_idx = self._component_affinity_matrix.argsort(axis = 1)

        for i, temp_component in enumerate(self._connected_components):
            for key in temp_component:
                for j in range(self._total_components):
                    component = self._connected_components[comp_sort_idx[i,j]]
                    for target in component:
                       comp_matrix[key,target] = float(j) + \
                                        float(distances[key,target])
        
        return comp_matrix

