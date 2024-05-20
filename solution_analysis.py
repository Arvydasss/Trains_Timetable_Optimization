"""
Solution analysis - file, which prints all the solutions of the problem (linear, simulated quantum, quantum)
example: python solution_analysis.py problem_number solution_type(console, png)
"""
import numpy as np
import sys

from encoders.ILP_encoder import printDeparture, solveLinearProblem, toHoursMinutes
from encoders.QUBO_encoder import earliestDepartureTime, indexingForQubo, makeQubo
from helpers.helpers_functions_PDF import trains_timings_to_pdf, trains_timings_to_png
from helpers.helpers_functions_QUBO import energy, load_train_solution
from helpers.helpers_functions import getProblem, generateProblem
from problems.read_files_to_problem import readScheduleXml


def visualise_solution(solution, Problem, num_brackets):
    """
    Function to print solution using QUBO matrix
    """
    trains_routes = Problem.trains_routes
    trains_timing = Problem.trains_timing
    inds, q_bits = indexingForQubo(trains_routes,trains_timing, Problem.d_max)
    print("n.o. x vars", q_bits)
    print("n.o. all var", np.size(solution))

    print("-" * num_brackets + "TRAIN SCHEDULE" + "-" *num_brackets)

    for i in range(q_bits):
        if solution[i] == 1:
            t = inds[i]["t"]
            s = inds[i]["s"]
            d = inds[i]["d"]
            time = d + earliestDepartureTime(trains_routes["Routes"], Problem.trains_timing, t, s)
            print("Train", t, "goes from station", s, "(dep. time)", toHoursMinutes(int(time)), " with ", d, " minutes delay (original time", toHoursMinutes(int(earliestDepartureTime(trains_routes["Routes"], Problem.trains_timing, t, s))),")")
    print("-" * 74)

def print_no_solutions(solutions, occurrences, Q_only_hard, offset):
    """ 
    Function to print n.o. all solutions and feasible solutions
    """
    count = 0
    epsilon = 0.00001
    l = len(solutions)
    for i in range(l):
        if energy(solutions[i], Q_only_hard) <= offset + epsilon:
            count = count + occurrences[i]
    print("n.o. solutions all = ", np.sum(occurrences) , "distinct =", l, "feasible = ", count)

def print_solutions(f, Q, Q_only_hard, offset, Problem_original, i=""):
    """
    Function to print problem solution (energies and train schedule)
    """
    solutions, energies, occurrences = load_train_solution(f, i)
    print("lowest energy")
    print("   from file = ", energies[0])
    print("   from QUBO = ", energy(solutions[0], Q))
    print_no_solutions(solutions, occurrences, Q_only_hard, offset)
    visualise_solution(solutions[0], Problem_original, 30)

def print_quantum_trains_timings(Problem_original, problem_number, Q_only_hard, f_Q, num_brackets, offset):
    """
    Function to print problem solution using quantum annealing
    """
    print(">" * num_brackets + "QUANTUM SOLVER RESULTS" + "<" * num_brackets)
    Q = np.load(f_Q)["Q"]
    for i in [3,3.5,4,4.5]:
         f = f"files/dwave_data/QUBO_complete_sol_real_anneal_problem{problem_number}_numread2000_antime240_chainst{i}"
         print_solutions(f, Q, Q_only_hard, offset, Problem_original, i)
    print(">" * num_brackets + "SOLVED BY QUANTUM SOLVER" +"<" * num_brackets)
    print("\n")

def print_simulated_trains_timings(Problem_original, Q_only_hard, f_Q, num_brackets, problem_number, offset):
    """
    Function to print problem solution using simulated quantum annealing
    """
    Q = np.load(f_Q)["Q"]
    print(">" * num_brackets + "SIMULATED SOLVER RESULTS" + "<" * num_brackets)
    f = f"files/QUBO_complete_sol_sim_anneal{problem_number}"
    print_solutions(f, Q, Q_only_hard, offset, Problem_original)
    print(">" * num_brackets + "SOLVED BY SIMULATED SOLVER" +"<" * num_brackets)
    print("\n")

def print_linear_trains_timings(problem, num_brackets):
    """
    Function to print problem solution using linear annealing
    """
    start_message = "SOLVING BY LINEAR SOLVER"
    end_message = "SOLVED BY LINEAR SOLVER"
    print(">" * num_brackets + start_message + "<" * num_brackets)
    prob, optimization_time = solveLinearProblem(problem)
    # print("optimisation, time = ", optimization_time, "seconds")

    print("-" * num_brackets + "TRAIN SCHEDULE" + "-" *num_brackets)
    for train_id in problem.trains_routes["T"]:
        for station in problem.trains_routes["Routes"][train_id]:
            printDeparture(problem.trains_routes, problem.trains_timing, prob, train_id, station)

    print("-" * 74)
    print(">" * num_brackets + end_message + "<" * num_brackets)
    print("\n")

def print_all_solutions(problem, QMatrix, problem_file, problem_number, solution_type):
    """
    Function to print all problem solutions (linear, simulated, quantums)
    """
    if (solution_type == 'console'):
        trains_timings_to_console(problem, problem_number, QMatrix, problem_file)
    else:
        trains_timings_to_pdf(problem, problem_file, problem_number)
        trains_timings_to_png(problem, problem_file, problem_number)

def trains_timings_to_console(problem, problem_number, QMatrix, problem_file):
    print_linear_trains_timings(problem, 30)
    print_simulated_trains_timings(problem, QMatrix, problem_file, 30, problem_number, offset = -12.5)
    print_quantum_trains_timings(problem, problem_number, QMatrix, problem_file, 30, -12.5)

if __name__ == "__main__":
    problem_number = int(sys.argv[1]) 
    solution_type = str(sys.argv[2]) 
    output_xml_file = f"data/LDZ_timetable_filtered{problem_number}.xml"
    generateProblem(problem_number, output_xml_file)
    taus, trains_timing, trains_routes = readScheduleXml(output_xml_file)
    
    prob = getProblem(problem_number, taus, trains_timing, trains_routes)
    prob_file = f'files/QUBO_matrix{problem_number}.npz'
    Q = makeQubo(prob)

    print_all_solutions(prob, Q, prob_file, problem_number, solution_type)
