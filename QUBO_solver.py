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
import dwave.inspector


def annealingSolution(problem):
    """
    Function to create a binary quadratic model from a QUBO problem
    """
    Q_init = np.load(f'files/QUBO_matrix{problem}.npz')
    Q = Q_init['Q'].astype(np.float32)
    model = dimod.BinaryQuadraticModel(Q, "BINARY")
    qubo, offset = model.to_qubo()
    return qubo

def simAnnealing(problem):
    """
    Function to get the SIMULATED annealing results
    """
    s = neal.SimulatedAnnealingSampler()
    sampleset = s.sample_qubo(annealingSolution(problem), beta_range=(5,100), num_sweeps=4000, num_reads=1000, beta_schedule_type='geometric')

    total_time_ns = sampleset.info['timing']['preprocessing_ns'] + \
                    sampleset.info['timing']['sampling_ns'] + \
                    sampleset.info['timing']['postprocessing_ns']
    total_time_ms = total_time_ns / 1e6 

    print(f"optimization time: {total_time_ms}")
    return sampleset

def realAnnealing(num_reads, annealing_time, chain_strength, problem):
    """
    Function to get the QUANTUM annealing results
    """
    sampler = EmbeddingComposite(DWaveSampler(token = 'DEV-45632b5020d7c79863b38f205ccd363e6dd48a05'))
    sampleset = sampler.sample_qubo(annealingSolution(problem), num_reads=num_reads, auto_scale='true', annealing_time=annealing_time, chain_strength=chain_strength) #annealing time in micro second, 20 is default.
   
    proraming_time_ms = sampleset.info['timing']['qpu_access_time']
    access_time_ms = sampleset.info['timing']['qpu_access_time']

    print(f"access time: {access_time_ms}, programing time: {proraming_time_ms}")
    return sampleset

def annealingResults(problem, annealing, num_reads, annealing_time):
    """
    Function to select annealing acording to what problem was selected
    """
    print('------------STARTING--------------')
    print(f'Settings model, solving with {annealing} annealing')

    if annealing == 'simulated':
        
        sampleset = simAnnealing(problem)         
        results=[]
        for datum in sampleset.data():
            x = dimod.sampleset.as_samples(datum.sample)[0][0]
            results.append((x, datum.energy))

        sdf = sampleset.to_serializable()
        with open(f"files/QUBO_complete_sol_sim_anneal{problem}", 'wb') as handle:
            pickle.dump(sdf, handle)
        with open(f"files/QUBO_samples_sol_sim_anneal{problem}", 'wb') as handle:
            pickle.dump(results, handle)

    elif annealing == 'quantum':
        for chain_strength in [3,3.5,4,4.5]:
            sampleset = realAnnealing(num_reads, annealing_time, chain_strength, problem)
            results=[]

            for datum in sampleset.data():
                x = dimod.sampleset.as_samples(datum.sample)[0][0]
                results.append((x, datum.energy))

            sdf = sampleset.to_serializable()
            fname_comp = f"files/dwave_data/QUBO_complete_sol_real_anneal_problem{problem}_numread{num_reads}_antime{annealing_time}_chainst{chain_strength}"
            fname_samp = f"files/dwave_data/QUBO_samples_sol_real_anneal_problem{problem}_numread{num_reads}_antime{annealing_time}_chainst{chain_strength}"

            os.makedirs(os.path.dirname(fname_comp), exist_ok = True)
            os.makedirs(os.path.dirname(fname_samp), exist_ok=True)

            with open(fname_comp, 'wb') as handle:
                pickle.dump(sdf, handle)

            with open(fname_samp, 'wb') as handle:
                pickle.dump(results, handle)

            print('Energy {} with chain strength {} run'.format(sampleset.first, chain_strength))
    
    print('------------END--------------')

problem = int(sys.argv[1])
annealing = str(sys.argv[2])
num_reads = int(sys.argv[3]) 
annealing_time = int(sys.argv[4]) 

annealingResults(problem, annealing, num_reads, annealing_time)