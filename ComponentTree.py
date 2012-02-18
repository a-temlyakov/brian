__author__ = """    Andrew Temlyakov (temlyaka@email.sc.edu)    """

from Node import *
from Components import *
import copy
import os

class ComponentTree(object):
    def __init__(self, base_affinity_matrix, proc_affinity_matrix, key_list):
        self.base_affinity_matrix = base_affinity_matrix
        self.proc_affinity_matrix = proc_affinity_matrix
        self.key_list = key_list
        self.root_id = None        
        self.nodes = {}
        
    def find_instance(self, instance, sim_list):
        if self.root_id is None:
            print "Tree does not exist. Building tree..."
            self.build_tree()

        best_node = self.root_id
        best_node_found = False

        while best_node_found is False:
            children = self.nodes[best_node]._children
            best_node = self._find_best_node(children, instance, sim_list)
            
            if best_node is None:
                best_node = self.nodes[children[0]]._parent
                best_node_found = True

            if self.nodes[best_node].confidence == 1.0:
                best_node_found = True

        return best_node

    def _find_best_node(self, children, index, sim_list):
        min_score = 1e6
        best_node = None
        for child in children:
            p_id = self.nodes[child].prototype_id
            sim_score = sim_list[p_id]
            #sim_score = self.base_affinity_matrix[index, p_id]
            if sim_score <= self.nodes[child].max_distance and \
                sim_score < min_score:
               min_score = sim_score
               best_node = child
        
        return best_node

    def build_tree(self):
        """ Recursive top-down (start at root) construction 
            of a tree. This construction is static, i.e. it
            is built from the same processed pair-wise matrix,
            the relationships do not change based on the level
            of the tree.
        """
        self.build_tree_dynamic()

    def build_tree_dynamic(self):
        """ Non-recursive bottom-up construction of the tree;
            at each level the pair-wise relationships are updated
            between components - where the instances inside components
            influence each others relationship to instances in other
            components
        """
        node_id = 0
        c = Components(self.proc_affinity_matrix)
        #Build the bottom level
        components, comp_mat = c.get_components(0.0, self.proc_affinity_matrix)
        for component in components:
            base_mat = self.base_affinity_matrix[component,:][:,component]
            proc_mat = self.proc_affinity_matrix[component,:][:,component]
            keys = self.key_list[component]
            n = Node(component, keys, base_mat, proc_mat, node_id)
            self.nodes[node_id] = n
            node_id += 1

        thresholds = asanyarray(range(1,11))/10.
        node_offset = temp_offset = 0
        for thresh in thresholds:
            temp_offset += len(components) 
            c = Components(comp_mat)
            components, comp_mat = c.get_components(thresh, comp_mat)
            for component in components:
                instances = []
                for instance in component:
                    idx = instance + node_offset
                    self.nodes[idx]._parent = node_id
                    instances += self.nodes[idx].list_of_instances
                base_mat = self.base_affinity_matrix[instances,:][:,instances]
                proc_mat = self.proc_affinity_matrix[instances,:][:,instances]
                
                keys = self.key_list[instances]
                n = Node(instances, keys, base_mat, proc_mat, node_id)
                n._children = list(asanyarray(component) + node_offset) 
                self.nodes[node_id] = n
                node_id += 1
  
            node_offset = temp_offset
        self.root_id = node_id - 1
        self._clean_tree()

    def _clean_tree(self):
        """ Initial tree construction has nodes that have a link of
            single children: 
            o
           / \
           o  ...
           |
           o
           |
           o
           |
          ...

            This method cleans the tree to remove such links:
            o
           / \
           o  ...
           |
           ...
        """
        nodes = copy.deepcopy(self.nodes)
        for key in self.nodes:
            node = nodes[key]
            if len(node._children) == 1:
                nodes[node._children[0]]._parent = node._parent
                
                #Update the children of the parent
                #Replace the node_id of the current node with its children
                nodes[node._parent]._children.remove(node.node_id)
                nodes[node._parent]._children += node._children
                
                del nodes[key]

        self.nodes = nodes

    def dump_tree_to_directory(self, S, n_id, in_path, out_path):
        node_instances = self.nodes[n_id].list_of_instances

        for instance in node_instances:
            s_name = self._get_shape_name(S, instance, 20)
            command = 'ln -s ' + in_path + '/' + s_name + '.gif ' + out_path
            os.system(command)

        if not self.nodes[n_id]._children:
            #no children exist, must be a leaf
            return -1
        else:
            node_keys = self.nodes[n_id]._children
            node_instances = self.nodes[n_id].list_of_instances

            for key in node_keys:
                o_path = out_path + '/' + str(key)
                os.system('mkdir ' + o_path)

                n_keys = self.nodes[key]._children
                self.dump_tree_to_directory(S, key, in_path, o_path)
            return 1

    def _get_shape_name(self, S, index, total_shapes):
        shape_idx = int(ceil(float(index+1)/float(total_shapes)))
        shape_num = (index+1) - total_shapes * shape_idx + total_shapes

        shape_name = S[shape_idx-1] + '-' + str(shape_num)
        return shape_name
