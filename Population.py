__author__ = """    Andrew Temlyakov (temlyaka@email.sc.edu)    """

from numpy import *
from Evaluation import *

#Used for diffirent similarity measures
#from scipy.spatial.distance import *

#Used for progress bar
import sys
import ProgressBar as pb

class Population(Evaluation):
    def __init__(self, affinity_matrix, instances_per_class, num_classes, \
                 types=None):
        Evaluation.__init__(self, affinity_matrix, instances_per_class, \
                            num_classes, types)
        self.affinity_matrices["processed_matrix"] = None

    def bullseye(self, total_instances=1, matrix_name = None):
        if matrix_name is None:
            super(Population, self).bullseye(total_instances, 
                                             "processed_matrix")
        else:
            super(Population, self).bullseye(total_instances, matrix_name)
    
    def print_self(self, matrix_name = None):
        if matrix_name is None:
            super(Population, self).print_self("processed_matrix")
        else:
            super(Population, self).print_self(matrix_name)

    def generate_diff(self, method="dice", k=20):
        """ Given a similarity matrix generate a 
            new similarity matrix based on the similarity
            of the top k closest matches for each pair of 
            shape instances
        """

        base_matrix = self.affinity_matrices["base_matrix"]
        processed_matrix = zeros_like(base_matrix)
        
        #Fixed k
        idx_top_k = base_matrix.argsort(axis = 1)[:, 0:k]
        
        #Progress bar stuff
        prog = pb.progressBar(0, self.total_instances, 77)
        oldprog = str(prog)

        for i in range(self.total_instances):
            a = set(idx_top_k[i, 0:k])
            for j in range(i + 1, self.total_instances):
                b = set(idx_top_k[j, 0:k])
                
                if method is "dice":
                    distance = 1 - self._dice_set_diff(a, b)
                elif method is "jaccard":
                    distance = 1 - self._jaccard_set_diff(a, b) 
                else:
                    raise ValueError("Comparison algorithm not found. \
                                      Currently implemented: dice, jaccard")
                
                processed_matrix[i, j] = distance

            #More progress bar stuff
            prog.updateAmount(i)
            if oldprog != str(prog):
                print prog, '\r',
                sys.stdout.flush()
                oldprog = str(prog)
        print '\n'
        
        processed_matrix += processed_matrix.transpose()
        self.affinity_matrices["processed_matrix"] = processed_matrix
        return processed_matrix

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

    def _dice_score(self, k):
        """ generator creates all possible discrete values
            that the dice score can become given a fixed k
        """
        dice_score = 0
        inc_frac = 1/float(k)

        while dice_score <= 1:
            yield dice_score
            dice_score += inc_frac

    
    def _get_k(self, row):
        pass

    def _build_histogram(self, sim_row):
        """ This method computes a histogram for a similarity row, 
            where bins are determined by standard deviations of the 
            pair-wise similarities for a given template instance 
        """    
        num_sd = 4
        mu = mean(sim_row)
        sd = std(sim_row)
        v = var(sim_row)

        #print "mu: ", mu, "std: ", sd, "var: ", v
    
        hist = zeros(16)

        for j in range(len(hist)):
            hist[j] = sum([s < mu - num_sd*sd for s in sim_row]) - sum(hist)
            num_sd = num_sd - 0.25

        return hist 
 
    def _plot_histogram(self, histogram):
        pos = arange(len(histogram))
        pl.bar(pos, histogram, 1.0, color='b')
        pl.show() 

    def _balance_histograms(self):       
 
        for i in range(self.total_instances):
            #print "i:", i
            histogram = self._build_histogram(self.similarity_matrix[i,:])
            #print histogram
            #self._plot_histogram(histogram)
    
            max_cost = -inf
            num_bins = 1

            for j in range(2, len(histogram)+1):
                #Explicitely create deep copies,
                #Getting shallow copies, otherwise (Python 2.6)
                temp_hist = histogram.copy()[:j]
                mu = ceil(mean(temp_hist))
                cost = 0
                while(max(temp_hist) > mu):
                    max_list = where(max(temp_hist) == temp_hist)[0]
                    min_list = where(min(temp_hist) == temp_hist)[0]

                    #Weight points on distance 
                    #cost += min_list[-1] - max_list[0]
                    
                    #Cost is 1 regardless of distance
                    if min_list[-1] > max_list[0]:
                        cost += 1
                    else:
                        cost -= 2
                                
                    temp_hist[min_list[-1]] += 1
                    temp_hist[max_list[0]] -= 1

                if cost > max_cost:
                    max_cost = cost
                    num_bins = j

            k = sum(histogram[:num_bins])
            self._cost_list[i] = max_cost 
            self._num_bins_list[i] = num_bins
            self._k_list[i] = k   
