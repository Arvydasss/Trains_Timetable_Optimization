"""
QUBO_generator - file to generate QUBO matrixes for problem
example: python QUBO_generator.py
"""
import numpy as np

from encoders.QUBO_encoder import makeQubo
from helpers.helpers_functions import getProblem
from solution_analysis import readScheduleXml

def analyseQubo(Q):
    """
    Function analyse degree of completness of the graph represented by symmetric QUBO matrix
    """
    s = np.size(Q,0)
    k = 0
    for i in range(s):
        for j in range(i+1, s):
            if Q[i][j] != 0.:
                k = k+1

    print("n.o. qbits = ", s)
    print("n.o. edges = ", k)
    full = (s-1)*s/2
    print("n.o. edges, full graph", full)
    print("density vs. full graph", k/full)
    print(".................................")

def saveMatrix():
    """
    Function to make and save QUBO matrix as file
    """
    xml_file = "data/LDZ-train_example_filtered.xml"
    taus, trains_timing, trains_routes = readScheduleXml(xml_file)
    prob = getProblem(taus, trains_timing, trains_routes)
    file = f'files/QUBO_matrix.npz'
    print("---------graph analysis---------")
    Q = makeQubo(prob)
    analyseQubo(Q)
    print(f"save QUBO matrix file to {file}")
    np.savez(file, Q=Q)

if __name__ == "__main__":
    saveMatrix()
