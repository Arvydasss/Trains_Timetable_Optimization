"""
Helpers for problems
"""
from problems.railway_problems import Problem

def getProblem(taus, trains_timing, trains_routes):
    problem_instance = Problem(taus, trains_timing, trains_routes)
    with open('problems/problem.xml', 'w') as file:
        file.write(str(problem_instance))
    
    return problem_instance