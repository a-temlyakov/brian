__author__ = """    Andrew Temlyakov (temlyaka@email.sc.edu)    """

from numpy import *

class Evaluation(object):
    def __init__(self, affinity_matrix, instances_per_class, num_classes, \
                 types=None):
        #Check all input
        if(type(affinity_matrix).__name__ != 'ndarray'):
            raise ValueError("Similarity matrix must be a numpy array.")
        if(instances_per_class <= 0):
            raise ValueError("Must have at least 1 instance per class.")
        if(num_classes <= 0):
            raise ValueError("Must have at least 1 class of instances.")
        
        #Public variables
        self.affinity_matrix = affinity_matrix
        self.instances_per_class = instances_per_class
        self.number_of_classes = num_classes
        self.total_instances = len(affinity_matrix)
        
        if types is not None:
            self.types = types
                
        #Private variables (values may change)
        self._similarity_score = 0.
        self._class_accuracy = zeros(self.total_instances)
     
    def print_self(self):
        print "----------------------"
        print "| Public Variables:  |"
        print "----------------------"
        print "Similarity Matrix: \n", self.affinity_matrix
        print "Instances per Class: ", self.instances_per_class
        print "Number of Instance Classes: ", self.number_of_classes
        print ""
        print "----------------------"
        print "| Private Variables: |"
        print "----------------------"
        print "Similarity score: ", self._similarity_score
        print "Class accuracy: ", self._class_accuracy
                        
    def bullseye(self, top_instances = 1, matrix_name = None):
        """ Standard Bullseye test                        
            All classes have the same number of instances 
        """  
         
        #When obtaining bullseye for lower number of instances than there are
        #instances per class, need to divide by number of instances being
        #retrieved
        if(top_instances < self.instances_per_class):
            divisor = top_instances
        else:
            divisor = self.instances_per_class

        sort_idx = self.affinity_matrix.argsort(axis=1)
        idx_top_k = sort_idx[:, 0:top_instances]
        
        #class_accuracy = zeros(self.total_instances)
        query_top = 0
        for i in range(self.total_instances):
            if(mod(i,self.instances_per_class) == 0):
                query_top += self.instances_per_class
            query_bottom = query_top - self.instances_per_class
            res = [int(query_bottom <= v < query_top) for v in idx_top_k[i]] 
            
            self._class_accuracy[i] = float(sum(res)) / divisor
        
        self._similarity_score = mean(self._class_accuracy)
        #self._class_accuracy = class_accuracy
            
        return self._similarity_score

    def nn_classification(self):
        sort_idx = self.affinity_matrix.argsort(axis = 1)
        idx_top_k = sort_idx[:, 1]
        print idx_top_k
        
        correct = 0
        key_list = asanyarray(range(self.total_instances)) / \
                            self.instances_per_class
        for i in range(self.total_instances):
            if key_list[i] == key_list[idx_top_k[i]]:
                correct += 1

        return correct / float(self.total_instances)

def get_shape_name(shape_names, index, shapes_per_class):
    """ Returns an actual shape name, e.g. 'Bone-18'
    """
    shape_idx = int(ceil(float(index+1)/float(shapes_per_class)))
    shape_num = (index+1) - shapes_per_class * shape_idx + shapes_per_class

    shape_name = shape_names[shape_idx-1] + '-' + str(shape_num)
    return shape_name
