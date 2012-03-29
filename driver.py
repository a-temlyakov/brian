#! /usr/bin/env python

__author__ = """Andrew Temlyakov (temlyaka@email.cse.sc.edu)"""

from numpy import *
from Evaluation import *
from Population import *
from ComponentTree import *
from Components import *
import sys
import os
import cPickle as pickle

from scipy import stats

data_path = '/home/temlyaka/sandbox/data/'
print "Loading", sys.argv[1], "similarity matrix..."
#cost_mat = genfromtxt(data_path + '/cost_matrices/' + sys.argv[1])

#cost_mat = load(data_path + '/cost-matrices/' + sys.argv[1])
cost_mat = genfromtxt(data_path + '/cost-matrices/' + sys.argv[1])
cost_mat = (cost_mat + cost_mat.transpose()) / 2.0

e = Evaluation(cost_mat, 20, 70)
#print e.nn_classification()

e.bullseye(40, "base_matrix")
print "Bullseye: ", e._similarity_score

#key_list = array([], int)
#for i in range(70):
#    key_list = append(key_list, (asanyarray(range(20)) / 20) + i)

#p = Population(cost_mat, 75, 15)
p = Population(cost_mat, 20, 70)
processed_matrix = p.generate_diff()

c = Components(processed_matrix)
c.get_components(0.3, strongly_connected=True)
comp_mat = c._expand_component_difference()
cp = Evaluation(comp_mat, 20, 70)
cp.bullseye(40)
print cp._similarity_score
cp.bullseye(20)
print cp._similarity_score
sys.exit()

#p.bullseye(40, "base_matrix")
shape_idx = 14
base_matrix = p.affinity_matrices["base_matrix"]
hist = p._build_histogram(base_matrix[:,shape_idx])
p._plot_histogram(hist)

f = open(data_path + '/datasets/mpeg7.types')
S = []
for line in f:
    S.append(line[:-1])
f.close()

print get_shape_name(S, shape_idx, 20)
#print "Balancing histograms..."
#p._balance_histograms()
#print "cost_list", p._cost_list
#print "sum of cost list", sum(p._cost_list)
#print "mean k", mean(p._k_list)
#print "mode k", stats.mode(p._k_list)
#print "median k", median(p._k_list)
#print "Original Top 40: ", p._similarity_score
#p.bullseye(20, "base_matrix")
#print "Original Top 20: ", p._similarity_score
#e.print_self("base_matrix")
#print "Generating diff..."
#processed_matrix = p.generate_diff(method="dice", k=13)
#p.bullseye(40, "processed_matrix")
#print "Processed Top 40: ", p._similarity_score
#p.bullseye(20, "processed_matrix")
#print "Processed Top 20: ", p._similarity_score

#print p.nn_classification()

#sys.exit()


#print "TREE METHODS FOLLOW"
#ctree = ComponentTree(cost_mat, processed_matrix, key_list, 13)
#ctree.build_tree("dynamic")

#print "Dumping tree to directory..."

#os.system('mkdir tree_dynamic')
#ctree.dump_tree_to_directory(S, ctree.root_id,
#                             data_path + '/datasets/mpeg7/inverted',
#                             'tree_dynamic')



#cp = Evaluation(cm, 20, 70)
#cp.bullseye(40)
#print cp._similarity_score

#print "mean", mean(e._list_of_affinities)
#print "median", median(e._list_of_affinities)
#e.print_self("processed_matrix")

#ss_idsc = (ss_idsc + ss_idsc.transpose()) / 2.0
#asc = (asc + asc.transpose()) / 2.0

#list_of_diff = [idsc, ss_idsc, asc]

#bins = md.get_histogram(ss_idsc[1399,:])
#print bins

#md.balance_histogram(bins)

#class_accuracy = zeros(1400)

