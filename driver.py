#! /usr/bin/env python

__author__ = """Andrew Temlyakov (temlyaka@email.cse.sc.edu)"""

from numpy import *
from Evaluation import *
from Population import *
from ComponentTree import *
from Components import *
import sys
import os
#from MultiDiff import *
#from scipy import stats

data_path = '/home/temlyaka/Research/sandbox/data/'
print "Loading", sys.argv[1], "similarity matrix..."
cost_mat = genfromtxt(data_path + '/cost_matrices/' + sys.argv[1])
cost_mat = (cost_mat + cost_mat.transpose()) / 2.0

key_list = array([], int)
for i in range(70):
    key_list = append(key_list, (asanyarray(range(20)) / 20) + i)

p = Population(cost_mat, 20, 70)
p.bullseye(40, "base_matrix")
print "Original Top 40: ", p._similarity_score
p.bullseye(20, "base_matrix")
print "Original Top 20: ", p._similarity_score
#e.print_self("base_matrix")
print "Generating diff..."
processed_matrix = p.generate_diff(method="dice", k=15)
p.bullseye(40, "processed_matrix")
print "Processed Top 40: ", p._similarity_score
p.bullseye(20, "processed_matrix")
print "Processed Top 20: ", p._similarity_score

e = Evaluation(cost_mat, 20, 70)
print e.nn_classification()

print "TREE METHODS FOLLOW"
ctree = ComponentTree(cost_mat, processed_matrix, key_list)
ctree.build_tree()

f = open(data_path + '/datasets/mpeg7.types')
S = []
for line in f:
    S.append(line[:-1])
f.close()

os.system('mkdir tree')
ctree.dump_tree_to_directory(S, ctree.root_id,
                             data_path + '/datasets/mpeg7/inverted',
                             'tree')


#cp = Evaluation(cm, 20, 70)
#cp.bullseye(40)
#print cp._similarity_score

#print "mean", mean(e._list_of_affinities)
#print "median", median(e._list_of_affinities)
#e.print_self("processed_matrix")
 
#print "Running affinity propagation..."
#e.affinity_propagation("base_matrix")
#e.affinity_propagation()
#e = Components(processed_matrix)
#e.get_components(0.3)
#comp_mat = e._expand_component_difference()

#cp = Evaluation(comp_mat, 20, 70)
#cp.bullseye(40)
#print cp._similarity_score
#cp.bullseye(20)
#print cp._similarity_score

#e.get_component_size()
#e.print_self()
#e._component_to_all_diff()
#e.bullseye(40)
#print "Final Top 40: ", e._similarity_score
#e.bullseye(20)
#print "Final Top 20: ", e._similarity_score
#e.print_self()


#print "Balancing histograms..."
#d.balance_histograms()
#print "cost_list", d._cost_list
#print "sum of cost list", sum(d._cost_list)
#print "mean k", mean(d._k_list)
#print "mode k", stats.mode(d._k_list)
#print "median k", median(d._k_list)
#ss_idsc = (ss_idsc + ss_idsc.transpose()) / 2.0
#asc = (asc + asc.transpose()) / 2.0

#list_of_diff = [idsc, ss_idsc, asc]

#md = MultiDiff(list_of_diff)
#md.print_self()
#score = md.evaluate_choice(ones(1400)+1)
#print score

#bins = md.get_histogram(ss_idsc[1399,:])
#print bins

#md.balance_histogram(bins)

#list_of_scores = md.pick_best_result()
#score = md.evaluate_choice(list_of_scores)
#print score

#print list_of_diff[0]


#d_ss = Evaluation(diff_ss, 20, 70)
#d_ss.bullseye(10)
#print d_ss._similarity_score
#print d_ss._class_accuracy[1399]

#a = Evaluation(asc, 20, 70)
#a.bullseye(10)
#print a._similarity_score
#print a._class_accuracy[1399]

#class_accuracy = zeros(1400)

#for i in range(1400):
#    score = max(d._class_accuracy[i], d_ss._class_accuracy[i])
#    class_accuracy[i] = score

#print mean(class_accuracy)

#e.plot_scores(200, 201)
#e.print_self()
