"""
Helpers for problems
"""
import datetime

from problems.railway_problems import Problem

def getProblem(problem_number, taus, trains_timing, trains_routes):
    """
    Function to get problem by number
    """
    problem_instance = Problem(taus, trains_timing, trains_routes)
    
    return problem_instance

def toDateTime(minutes):
    """
    Function to change minutes to dateTime format
    """
    return datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(minutes=(int(minutes)))