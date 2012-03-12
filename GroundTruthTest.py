#! /usr/bin/env python

__author__ = """Andrew Temlyakov (temlyaka@email.cse.sc.edu)"""

from numpy import *
from Population import *
from ComponentTree import *
from Node import *

path = '/home/temlyaka/sandbox/data/cost-matrices/'
cost_mat = load(path + sys.argv[1])
cost_mat = (cost_mat + cost_mat.transpose()) / 2.0

key_list = asanyarray(range(1400)) / 20
correct_count = 0

for idx in xrange(len(cost_mat)):
    nodes_list = []
    for j in xrange(70):
        start_idx = j * 20
        end_idx = start_idx + 20
        
        if j == idx / 20:
            instances = range(start_idx,idx) + range(idx+1, end_idx)
        else: 
            instances = range(start_idx,end_idx)
        
        base_mat = cost_mat[instances,:][:,instances]
        n = Node(instances, key_list[instances], base_mat, base_mat, j)
        nodes_list.append(n)

    min_score = inf
    found_idx = -1
    for node in nodes_list:
         score = cost_mat[idx,node.prototype_id]
         if score < min_score:
             min_score = score 
             found_idx = node.prototype_id 
    
         
    if key_list[found_idx] == key_list[idx]:
        correct_count += 1

print correct_count / 1400.
