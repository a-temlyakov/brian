__author__ = """    Andrew Temlyakov (temlyaka@email.sc.edu)    """

from Node import *
from Components import *
from Population import dice_fractions
from Evaluation import get_shape_name
import copy
import os

class ComponentTree(object):
    def __init__(self, base_affinity_matrix, 
                       proc_affinity_matrix, 
                       key_list,
                       fixed_k):

        self.base_affinity_matrix = base_affinity_matrix
        self.proc_affinity_matrix = proc_affinity_matrix
        self.key_list = key_list
        self.root_id = None        
        self.nodes = {}
        self.fixed_k = fixed_k

        self._inf = 1e6
    
    def get_instance(self, node_id, instance, sim_list):
        """ Check all paths whos prototype score
            with the template instance is less than
            the max score 
        
            TO-DO: Still potential bugs!!!
        """

        if self.root_id is None:
            raise ValueError("Tree does not exist.")

        children = self.nodes[node_id]._children

        if len(children) == 0:
            return self._inf, 0, -1

        best_nodes = {}    

        for child in children:
            p_id = self.nodes[child].prototype_id
            sim_score = sim_list[p_id]

            if sim_score <= self.nodes[child].max_distance:
                if self.nodes[child].confidence == 1.0:
                    return sim_score, len(children), child
                else:
                    best_nodes[child] = \
                        self.get_instance(child, instance, sim_list) 

        sum_comparisons = 0
        min_score = self._inf
        best_node = -1
        for key in best_nodes:
            sum_comparisons += best_nodes[key][1]

            if best_nodes[key][0] < min_score:
                min_score = best_nodes[key][0]
                best_node = key

        return min_score, sum_comparisons+len(children), best_node

        
        
    def find_instance(self, instance, sim_list):
        if self.root_id is None:
            print "Tree does not exist. Building tree..."
            self.build_tree()

        best_node = self.root_id
        best_node_found = False
        sum_comparisons = 0
        
        while best_node_found is False:
            children = self.nodes[best_node]._children
            
            if not children:
                break
            
            sum_comparisons += len(children)

            best_node = self._find_best_node(children, instance, sim_list)
            
            if best_node is None:
                best_node = self.nodes[children[0]]._parent
                best_node_found = True

            if self.nodes[best_node].confidence == 1.0:
                best_node_found = True

        return best_node, sum_comparisons

    def _find_best_node(self, children, index, sim_list):
        min_score = self._inf
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

    def build_tree(self, tree_type="static"):
        """ Entry build_tree function
        """

        if self.root_id is not None:
            """ Tree has been previously created
                Re-set all values to build a fresh tree
            """
            self.root_id = None
            self.nodes = {}

        if tree_type is "static":
            #print "Generating a top-down static tree!"
            self.root_id = 0
            idx_map = asanyarray(range(len(self.base_affinity_matrix)))
            self._build_tree_static(self.proc_affinity_matrix, \
                                    1.0, \
                                    None, \
                                    idx_map)
        elif tree_type is "dynamic":
            #print "Generating a bottom-up dynamic tree!"
            self._build_tree_dynamic()
        else:
            raise ValueError("Tree type does not exist! Currently Implemented: static, dynamic")
  
        #print "Cleaning tree..." 
        self._clean_tree() 

    def _build_tree_static(self, proc_mat, fraction, parent_id, idx_map):
        """ Recursive top-down (start at root) construction 
            of a tree. This construction is static, i.e. it
            is built from the same processed pair-wise matrix,
            the relationships do not change based on the level
            of the tree.
        """
    
        if fraction < 0:
            return

        c = Components(proc_mat)
        components = c.get_components(fraction, proc_mat)[0]

        for component in components:
            i_map = idx_map[component]
            b_mat = self.base_affinity_matrix[i_map,:][:,i_map]
            p_mat = self.proc_affinity_matrix[i_map,:][:,i_map]
            keys = self.key_list[i_map]
            n_id = len(self.nodes)
            
            n = Node(i_map, keys, b_mat, p_mat, n_id)
            n._parent = parent_id

            if parent_id is not None:
                self.nodes[parent_id]._children.append(n_id)
            
            self.nodes[n_id] = n
            
            fraction = fraction - 1/float(self.fixed_k)
            self._build_tree_static(p_mat, fraction, n_id, i_map)


    def _build_tree_dynamic(self):
        """ Non-recursive bottom-up construction of the tree;
            at each level the pair-wise relationships are updated
            between components - where the instances inside components
            influence each others relationship to instances in other
            components
        """
        node_id = 0
        fractions = dice_fractions(self.fixed_k)

        c = Components(self.proc_affinity_matrix)
        #Build the bottom level
        components, comp_mat = c.get_components(fractions.next(), 
                                                self.proc_affinity_matrix)
        for component in components:
            base_mat = self.base_affinity_matrix[component,:][:,component]
            proc_mat = self.proc_affinity_matrix[component,:][:,component]
            keys = self.key_list[component]
            n = Node(component, keys, base_mat, proc_mat, node_id)
            self.nodes[node_id] = n
            node_id += 1

        node_offset = temp_offset = 0
        for fraction in fractions:
            temp_offset += len(components) 
            c = Components(comp_mat)
            components, comp_mat = c.get_components(fraction, comp_mat)
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
          /|\
          ...

            This method cleans the tree to remove such links:
            o
           / \
           o  ...
          /|\ 
          ...
        """
        nodes = copy.deepcopy(self.nodes)
        for key in self.nodes:
            node = nodes[key]
            if len(node._children) == 1 and node._parent is not None:
                nodes[node._children[0]]._parent = node._parent
                
                #Update the children of the parent
                #Replace the node_id of the current node with its children
                nodes[node._parent]._children.remove(node.node_id)
                nodes[node._parent]._children += node._children
                
                del nodes[key]

        self.nodes = nodes

    def dump_tree_to_directory(self, shape_names, n_id, in_path, out_path):
        node_instances = self.nodes[n_id].list_of_instances

        for instance in node_instances:
            s_name = get_shape_name(shape_names, instance, 20)
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
                self.dump_tree_to_directory(shape_names, key, in_path, o_path)
            return 1

