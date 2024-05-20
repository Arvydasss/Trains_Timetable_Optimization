"""
Helpers for problems
"""
import datetime
import os

from problems.read_files_to_problem import filterScheduleXml
from problems.railway_problems import Problem

def getProblem(problem_number, taus, trains_timing, trains_routes):
    problem_instance = Problem(taus, trains_timing, trains_routes)
    output_file = f'problems/problem{problem_number}.xml'
    if os.path.exists(output_file):
        os.remove(output_file)

    with open(output_file, 'w') as file:
        file.write(str(problem_instance))
    
    return problem_instance

def generateProblem(problem, output_xml_file):
    xml_file = "data/LDZ_timetable.xml"

    trains = []
    stations = ['09180','09170','09280','09940','09960','09290','09303','09320','09330','09340','09350','09351','09355','09860','09764','09772','09750','09751','09780','09790','09800','09801','09736','09732','09730','09715','09730','09676','09670','09680','09540','09010','09150','09100','09160']
    if (problem == 1):
        trains = ['2001', '2056', '2410', '2102', '6001']
    if (problem == 2):
        trains = ['2001', '6001','3011', '2102', '2056', '3162', '3529']
    if (problem == 3):
        trains = ['3004', '1584','2102', '3162', '3164', '3529', '2101', '3011', '6711', '6004']

    filterScheduleXml(xml_file, output_xml_file, stations, trains)

def toDateTime(minutes):
    return datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(minutes=(int(minutes)))