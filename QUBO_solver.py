"""
Solver to solve the generated QUBO matrix, with diferent method
example: python Qfile_solve.py 'solver type(simulated, quantum)' 0 0 
"""
import pickle
import os
import time
import neal
import numpy as np
import dimod
import sys

from dwave.system import EmbeddingComposite, DWaveSampler
from helpers.helpers_functions import problemName

def annealingSolution():
    """
    Function to get qubo from file
    """
    Q_init = np.load(f'files/QUBO_matrix.npz')
    Q = Q_init['Q'].astype(np.float32)
    model = dimod.BinaryQuadraticModel(Q, "BINARY")
    qubo, offset = model.to_qubo()
    return qubo

def simAnnealing():
    """
    Function to get the SIMULATED annealing results
    """
    s = neal.SimulatedAnnealingSampler()
    start_time = time.time()
    sampleset = s.sample_qubo(annealingSolution(), beta_range=(5,100), num_sweeps=4000, num_reads=1000, beta_schedule_type='geometric')
    print("optimisation, time = ", time.time() - start_time, "seconds")
    return sampleset

def realAnnealing(num_reads, annealing_time, chain_strength):
    """
    Function to get the QUANTUM annealing results
    """
    sampler = EmbeddingComposite(DWaveSampler(token = 'DEV-75eac624dcb58d1ab3ca5c66c86cbe442f1030f8'))
    start_time = time.time()
    sampleset = sampler.sample_qubo(annealingSolution(), num_reads=num_reads, auto_scale='true', annealing_time=annealing_time, chain_strength=chain_strength) #annealing time in micro second, 20 is default.
    print("optimisation, time = ", time.time() - start_time, "seconds")
    return sampleset

def annealingResults(annealing, num_reads, annealing_time):
    """
    Function to select annealing acording to what problem was selected
    """
    print('------------STARTING--------------')
    print(f'{problemName} settings model, solving with {annealing} annealing')

    if annealing == 'simulated':
        
        sampleset = simAnnealing()         
        results=[]
        for datum in sampleset.data():
            x = dimod.sampleset.as_samples(datum.sample)[0][0]
            results.append((x, datum.energy))

        sdf = sampleset.to_serializable()
        with open(f"files/QUBO_complete_sol_sim-anneal", 'wb') as handle:
            pickle.dump(sdf, handle)
        with open(f"files/QUBO_samples_sol_sim-anneal", 'wb') as handle:
            pickle.dump(results, handle)

    elif annealing == 'quantum':
        for chain_strength in [3,3.5,4,4.5]:
            sampleset = realAnnealing(num_reads, annealing_time, chain_strength)
            results=[]

            for datum in sampleset.data():
                x = dimod.sampleset.as_samples(datum.sample)[0][0]
                results.append((x, datum.energy))

            sdf = sampleset.to_serializable()
            fname_comp = f"files/dwave_data/QUBO_complete_sol_real-anneal_numread{num_reads}_antime{annealing_time}_chainst{chain_strength}"
            fname_samp = f"files/dwave_data/QUBO_samples_sol_real-anneal_numread{num_reads}_antime{annealing_time}_chainst{chain_strength}"

            os.makedirs(os.path.dirname(fname_comp), exist_ok=True)
            os.makedirs(os.path.dirname(fname_samp), exist_ok=True)

            with open(fname_comp, 'wb') as handle:
                pickle.dump(sdf, handle)

            with open(fname_samp, 'wb') as handle:
                pickle.dump(results, handle)

            print('Energy {} with chain strength {} run'.format(sampleset.first, chain_strength))
    
    print()
    print('------------END--------------')

annealing = str(sys.argv[1])
num_reads = int(sys.argv[2]) 
annealing_time = int(sys.argv[3]) 

annealingResults(annealing, num_reads, annealing_time)