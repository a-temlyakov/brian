#! /usr/bin/env python

__author__ = """Andrew Temlyakov (temlyaka@email.cse.sc.edu)"""

from Evaluation import *
from Population import *
from Components import *

""" Load data into a numpy matrix.
    (1) load function is used to load a .npy binary file,
        which can be generated from a .txt file
    (2) genfromtxt generates a numpy array from a raw text
        file
"""
print "Loading", sys.argv[1], "similarity matrix..."
cost_mat = load(sys.argv[1])
#cost_mat = genfromtxt(data_path + '/cost-matrices/' + sys.argv[1])

""" Compute the bullseye score.
    Assuming MPEG-7 data is loaded
"""
e = Evaluation(cost_mat, 20, 70)
print "Top 40 bullseye score: ", e.bullseye(40)

""" Compute a new similarity matrix using dice coefficient
    as a population cue
"""
#Geometric mean, to ensure symmetry
cost_mat = sqrt(cost_mat * cost_mat.transpose())
p = Population(cost_mat, 20, 70, verbose=True)
#Not setting k will attempt to automatically find it!
processed_matrix = p.generate_diff(k=13) 

e = Evaluation(processed_matrix, 20, 70)
print "Top 40 bullseye score using dice: ", e.bullseye(40)

""" Update the similarity matrix further using the previous
    matrix to build components 
"""
c = Components(processed_matrix)
c.get_components(0.3, strongly_connected=False)
comp_mat = c._expand_component_difference()

e = Evaluation(comp_mat, 20, 70)
print "Top 40 bullseye score after components: ", e.bullseye(40)

