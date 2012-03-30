#! /usr/bin/env python

__author__ = """Andrew Temlyakov (temlyaka@email.cse.sc.edu)"""

from numpy import *
from Population import *
from ComponentTree import *

path = '/home/temlyaka/sandbox/data/cost-matrices/'
cost_mat = load(path + sys.argv[1])
cost_mat = (cost_mat + cost_mat.transpose()) / 2.0

#key_list = array([], int)
#for i in range(70):
#    key_list = append(key_list, (asanyarray(range(20)) / 20) + i)
key_list = asanyarray(range(1400)) / 20

start_idx = int(sys.argv[2])
end_idx = int(sys.argv[3])

for idx in range(start_idx, end_idx):
    #remove the rows and columns of instance under consideration
    temp_mat = delete(cost_mat, s_[idx], axis = 0)
    test_mat = delete(temp_mat, s_[idx], axis = 1)

    p = Population(test_mat, 20, 70)
    processed_matrix = p.generate_diff(method="dice", k=13, k_fixed=True)

    k_list = delete(key_list, idx)
    ctree = ComponentTree(test_mat, processed_matrix, k_list, 13)
    ctree.build_tree("bottomup")


    sim_list = delete(cost_mat[idx,:], idx)

    #print "Getting instance"
    #sim_score, bnode, sum_comparisons = \
        #ctree.get_instance(ctree.root_id, idx, sim_list)

    bnode, sum_comparisons = ctree.find_instance(idx, sim_list)

    #ctree.nodes[bnode].print_self()
    #print ctree.nodes[bnode]._max_key_idx, key_list[idx]
    if ctree.nodes[bnode]._max_key_idx == key_list[idx]:
        print "1", sum_comparisons
    else:
        print "0", sum_comparisons
