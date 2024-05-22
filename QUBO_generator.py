"""
QUBO_generator - file to generate QUBO matrixes for problem
example: python QUBO_generator.py
"""
import numpy as np
import sys

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
    print(".................................")

def saveMatrix(problem):
    """
    Function to make and save QUBO matrix as file
    """
    xml_file = f"data/LDZ_timetable_filtered{problem}.xml"
    taus, trains_timing, trains_routes = readScheduleXml(xml_file)
    prob = getProblem(problem, taus, trains_timing, trains_routes)
    file = f'files/QUBO_matrix{problem}.npz'
    print("---------graph analysis---------")
    Q = makeQubo(prob)
    analyseQubo(Q)
    print(f"save QUBO matrix file to {file}")
    np.savez(file, Q=Q)

if __name__ == "__main__":
    problem = int(sys.argv[1])
    saveMatrix(problem)
