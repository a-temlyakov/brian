__author__ = """    Andrew Temlyakov (temlyaka@email.sc.edu)    """

from numpy import *
import networkx as nx

class Node(object):
    def __init__(self, list_of_instances, 
                       keys, 
                       base_sim_matrix, 
                       proc_sim_matrix,
                       node_id):

        self.node_id = node_id
        self.list_of_instances = list_of_instances
        self.total_instances = len(list_of_instances)
        self.base_similarity_matrix = base_sim_matrix
        self.proc_similarity_matrix = proc_sim_matrix
        
        self._keys = keys
        self._max_key_idx = None
        self._prototype_idx = None
        self._parent = None
        self._children = []

    
    @property
    def prototype_id(self):
        if self._prototype_idx is None:
            if self.total_instances >= 3:
                self._prototype_idx = self._get_prototype_id()
            else:
                self._prototype_idx = 0
        return self.list_of_instances[self._prototype_idx]

    @property
    def max_distance(self):
        if self._prototype_idx is None:
            self.prototype_id

        return max(self.base_similarity_matrix[self._prototype_idx, :])
        #return self.base_similarity_matrix.max()

    @property
    def min_distance(self):
        return self.base_similarity_matrix.min()

    @property
    def confidence(self):
        """ This measures how many instances of the same class 
            are in the node """
        counts = bincount(self._keys)
        self._max_key_idx = argmax(counts)
        return counts[self._max_key_idx] / float(self.total_instances)

    def _get_prototype_id(self):
        node_graph = nx.Graph()

        for i in range(self.total_instances):
            for j in range(i + 1, self.total_instances):
                node_graph.add_edge(i, j, weight = \
                                    self.base_similarity_matrix[i, j])

        T = nx.minimum_spanning_tree(node_graph)
        list_of_centers = nx.center(T)
        return list_of_centers[0]

    def print_self(self):
        print "------------------------"
        print "Node Id: ", self.node_id
        print "List of Instances: ", self.list_of_instances
        print "Base Similarity Matrix: ", self.base_similarity_matrix
        print "Proc Similarity Matrix: ", self.proc_similarity_matrix
        print "Total Instances:", self.total_instances
        print "Prototype Id: ", self.prototype_id
        print "Max Distance: ", self.max_distance
        print "Min Distance: ", self.min_distance
        print "Confidence: ", self.confidence
        print "------------------------"
        print "Parent node: ", self._parent
        print "Children nodes: ", self._children
        print "Keys: ", self._keys
        print "Max Key Index: ", self._max_key_idx
        print "Prototype Index: ", self._prototype_idx
        print "------------------------"

