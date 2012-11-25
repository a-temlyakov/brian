__author__ = """    Andrew Temlyakov (temlyaka@gmail.com)    """

from numpy import *
import pylab as pl

#Used for progress bar
import sys
import ProgressBar as pb

class Population(object):
    def __init__(self, affinity_matrix, instances_per_class, num_classes, \
                 types=None, verbose=False):
        
        """ Check all input """
        if(type(affinity_matrix).__name__ != 'ndarray'):
            raise ValueError("Similarity matrix must be a numpy array.")
        if(instances_per_class <= 0):
            raise ValueError("Must have at least 1 instance per class.")
        if(num_classes <= 0):
            raise ValueError("Must have at least 1 class of instances.")
        
        """ Public variables """
        self.affinity_matrix = affinity_matrix
        self.processed_matrix = zeros_like(self.affinity_matrix)
        self.instances_per_class = instances_per_class
        self.number_of_classes = num_classes
        self.total_instances = len(self.affinity_matrix)
        self.verbose = verbose
        
        """ Private variables (values may change) """
        self._cost_list = [0] * self.total_instances
        self._bin_count_list = [0] * self.total_instances
        self._k_list = [0] * self.total_instances
    
    def print_self(self):
        print "----------------------"
        print "| Public Variables:  |"
        print "----------------------"
        print "Original Matrix: \n", self.affinity_matrix
        print "Processed Matrix: \n", self.processed_matrix
        print "Instances per Class: ", self.instances_per_class
        print "Number of Instance Classes: ", self.number_of_classes
        print "Verbose? ", self.verbose
        print ""
        print "----------------------"
        print "| Private Variables: |"
        print "----------------------"
        print "Cost list: ", self._cost_list
        print "Bin count list: ", self._bin_count_list
        print "K list: ", self._k_list

    def generate_diff(self, method="dice", 
                            k=None, 
                            lower_bound=None,
                            k_fixed=False, 
                            alpha=0.3):
        """ Given a similarity matrix generate a 
            new similarity matrix based on the similarity
            of the top k closest matches for each pair of 
            shape instances
        """
       
        if k is None:
            if self.verbose: print "k not set. Finding a good value..."
            k = self._get_k()
            if self.verbose: print "Found k:", k

        if k_fixed is True:
            k_i = k 
        else:
            upper_bound = k     
            if lower_bound is None: 
                lower_bound = int(upper_bound * alpha) + 1

        idx_top_k = self.affinity_matrix.argsort(axis = 1)[:, 0:k]
       
        if self.verbose:  
            print "Building new similarity matrix..." 
            """ start progress bar """
            prog = pb.progressBar(0, self.total_instances, 77)
            oldprog = str(prog)
            """ end progress bar """

        for i in xrange(self.total_instances):
            shape_ranks = idx_top_k[i, :]           
            for j in xrange(i + 1, self.total_instances):

                if k_fixed is not True:
                    j_idx = where(shape_ranks == j)[0]

                    if not j_idx:
                        k_i = upper_bound
                    else:
                        k_i = j_idx[0] + 1
                    
                        if k_i < lower_bound:
                            k_i = lower_bound
               
                a = set(idx_top_k[i, 0:k_i]) 
                b = set(idx_top_k[j, 0:k_i])
                
                if method is "dice":
                    distance = 1 - self._dice_set_diff(a, b)
                elif method is "jaccard":
                    distance = 1 - self._jaccard_set_diff(a, b) 
                else:
                    raise ValueError("Comparison algorithm not found. \
                                      Currently implemented: dice, jaccard")
                
                self.processed_matrix[i, j] = distance

            if self.verbose:
                """ start progress bar """
                prog.updateAmount(i)
                if oldprog != str(prog):
                    print prog, '\r',
                    sys.stdout.flush()
                    oldprog = str(prog)
            """ end progress bar """
        
        if self.verbose: print '\n'
        self.processed_matrix += self.processed_matrix.transpose()
        return self.processed_matrix

    def _dice_set_diff(self, a, b):
        """ Compute the Dice's similarity of sets a and b """
        set_intersection = a & b;
        dice_index = 2 * len(set_intersection) / float(len(a) + len(b))
        return dice_index
 
    def _jaccard_set_diff(self, a, b):
        """ Compute the Jaccard similarity of sets a and b """
        set_intersection = a & b
        set_union = a | b
        jaccard_index = float(len(set_intersection)) / float(len(set_union))
        return jaccard_index

    def _get_k(self):
        self._balance_histograms()        
        return int(mean(self._k_list))

    def _build_histogram(self, sim_row, num_bins=16, bin_width=0.25):
        """ This method computes a histogram for a similarity row, 
            where bins are determined by standard deviations of the 
            pair-wise similarities for a given template instance 
        
            Computes only the left side of the histogram, that is
            all similarities that are less than the mean
        """    
        num_sd = int(num_bins * bin_width)
        
        mu = mean(sim_row)
        sd = std(sim_row)
    
        hist = zeros(num_bins+2)

        for j in xrange(len(hist)):
            hist[j] = sum([s < mu - num_sd*sd for s in sim_row]) - sum(hist)
            num_sd = num_sd - bin_width

        return hist 
 
    def _plot_histogram(self, histogram):
        """ Used this method to get some histogram plots for
            my dissertation. It's very rough and likely needs tweaking, 
            but keeping it here for reference.
        """
        pos = arange(len(histogram))
        pl.bar(pos, histogram, 0.90, color='b')
        pl.xticks(pos+0.90/2., ('-4','','','',
                                '-3','','','',
                                '-2','','','',
                                '-1','','','',
                                '0'))
        pl.ylabel('Bin Size')
        pl.xlabel('Number of standard deviations away from the mean')
        pl.show() 

    def _balance_histograms(self):    
        """ Compute the cost of balancing a histogram for each
            row in the affinity matrix
        """
        
        if self.verbose:   
            """ start progress bar """
            prog = pb.progressBar(0, self.total_instances, 77)
            oldprog = str(prog)
            """ end progress bar """
 
        for i in xrange(self.total_instances):
            histogram = self._build_histogram(self.affinity_matrix[i,:])
    
            max_cost = -inf
            bin_count = 1

            for j in xrange(2, len(histogram)+1):
                """ Explicitely create deep copies,
                    Getting shallow copies, otherwise (Python 2.6)
                """
                temp_hist = histogram.copy()[:j]
                mu = ceil(mean(temp_hist))
                cost = 0
                while(max(temp_hist) > mu):
                    max_list = where(max(temp_hist) == temp_hist)[0]
                    min_list = where(min(temp_hist) == temp_hist)[0]

                    """ Cost is 1 regardless of distance """
                    if min_list[-1] > max_list[0]:
                        cost += 1
                    else:
                        cost -= 2
                                
                    temp_hist[min_list[-1]] += 1
                    temp_hist[max_list[0]] -= 1

                if cost > max_cost:
                    max_cost = cost
                    bin_count = j

            k = sum(histogram[:bin_count])
            self._cost_list[i] = max_cost 
            self._bin_count_list[i] = bin_count
            self._k_list[i] = k 
        
            if self.verbose:            
                """ start progress bar """
                prog.updateAmount(i)
                if oldprog != str(prog):
                    print prog, '\r',
                    sys.stdout.flush()
                    oldprog = str(prog)
                """ end progress bar """
        if self.verbose: print '\n'            
             
def dice_fractions(k):
    """ generator creates all possible discrete values
        that the dice score can become given a fixed k
        e.g. k=4 -> [0.0, 0.25, 0.5, 0.75, 1.0]

        Note: this is not part of the class and can be
              imported seperately.
    """

    for i in xrange(k+1):
        dice_score = i / float(k)
        yield dice_score

