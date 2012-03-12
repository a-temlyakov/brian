__author__ = """    Andrew Temlyakov (temlyaka@email.sc.edu)    """

from numpy import *
from scipy import stats
from Evaluation import *
import pylab as pl

#Used for progress bar
import sys
import ProgressBar as pb



class Population(Evaluation):
    def __init__(self, affinity_matrix, instances_per_class, num_classes, \
                 types=None):
        Evaluation.__init__(self, affinity_matrix, instances_per_class, \
                            num_classes, types)
        self.affinity_matrices["processed_matrix"] = None

        self._cost_list = [0] * self.total_instances
        self._num_bins_list = [0] * self.total_instances
        self._k_list = [0] * self.total_instances

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
        #prog = pb.progressBar(0, self.total_instances, 77)
        #oldprog = str(prog)

        for i in xrange(self.total_instances):
            a = set(idx_top_k[i, 0:k])
            for j in xrange(i + 1, self.total_instances):
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
            #prog.updateAmount(i)
            #if oldprog != str(prog):
                #print prog, '\r',
                #sys.stdout.flush()
                #oldprog = str(prog)
        #print '\n'
        
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

    def _get_k(self):
        K_list = []
        for i in xrange(self.total_instances):
            sim_row = self.affinity_matrices["base_matrix"][i, :]

            """ delete the score with itself (0) """
            sim_row = delete(sim_row, i)

            mu = mean(sim_row)
            sd = std(sim_row)

            K_list.append(sum([s < (mu - 2*sd) for s in sim_row]))

        return stats.mode(K_list), median(K_list), mean(K_list)

    def _build_histogram(self, sim_row):
        """ This method computes a histogram for a similarity row, 
            where bins are determined by standard deviations of the 
            pair-wise similarities for a given template instance 
        
            Computes only the left side of the histogram, that is
            all similarities that are less than the mean
        """    
        num_bins = 16
        bin_width = 0.25
        num_sd = int(num_bins * bin_width)

        mu = mean(sim_row)
        sd = std(sim_row)
        v = var(sim_row)

        #print "mu: ", mu, "std: ", sd, "var: ", v
    
        hist = zeros(num_bins+2)

        for j in range(len(hist)):
            hist[j] = sum([s < mu - num_sd*sd for s in sim_row]) - sum(hist)
            num_sd = num_sd - bin_width

        return hist 
 
    def _plot_histogram(self, histogram):
        pos = arange(len(histogram))
        pl.bar(pos, histogram, 0.90, color='b')
        pl.xticks(pos+0.90/2., ('-4','','','','-3','','','','-2','','','','-1','','','','0'))
        pl.ylabel('Bin Size')
        pl.xlabel('Number of standard deviations away from the mean')
        pl.show() 

    def _balance_histograms(self):       
        base_matrix = self.affinity_matrices["base_matrix"]
 
        for i in range(self.total_instances):
            #print "i:", i
            histogram = self._build_histogram(base_matrix[i,:])
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

