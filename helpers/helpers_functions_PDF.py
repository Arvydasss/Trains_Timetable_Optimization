"""
Helpers for PDF formating
"""
import numpy as np
from reportlab.lib.pagesizes import letter
import os

from encoders.ILP_encoder import solveLinearProblem, getDepartureArrivalInfoForPdf, toHoursMinutes
from encoders.QUBO_encoder import earliestDepartureTime, indexingForQubo
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

from helpers.helpers_functions_QUBO import load_train_solution

def trains_timings_to_pdf(problem, problem_file):
    trains_timings_orginal_to_pdf(problem)
    trains_timings_linear_to_pdf(problem)
    trains_timings_simulated_to_pdf(problem, problem_file)

def trains_timings_orginal_to_pdf(problem):
    """
    Function to print problem original timetable to a PDF file
    """
    output_file = "train_schedule_original.pdf"
    prob, optimization_time = solveLinearProblem(problem)

    if os.path.exists(output_file):
        os.remove(output_file)

    doc = SimpleDocTemplate(output_file, pagesize=letter)
    
    header_row = ["Traukinys", "Stotis", "Atvykimo laikas", "Išvykimo laikas", "Stotis", "Atvykimo laikas", "Išvykimo laikas"]
    table_data = [header_row]

    for train_id in problem.trains_routes["T"]:
        isFirstStation = True
        route = problem.trains_routes["Routes"][train_id]
        for i in range(0, len(route), 2): 
            station1 = route[i]
            station2 = route[i + 1] if i + 1 < len(route) else None
            train_schedule = [train_id]
            departure_info1 = getDepartureArrivalInfoForPdf(problem.trains_routes, problem.trains_timing, prob, train_id, station1, isFirstStation)
            train_schedule.append(station1)
            train_schedule.append(departure_info1["conflicted_arrival_time"])
            train_schedule.append(departure_info1["conflicted_departure_time"])
            if station2:
                departure_info2 = getDepartureArrivalInfoForPdf(problem.trains_routes, problem.trains_timing, prob, train_id, station2, isFirstStation)
                train_schedule.append(station2)
                train_schedule.append(departure_info2["conflicted_arrival_time"])
                train_schedule.append(departure_info2["conflicted_departure_time"])
            else:
                train_schedule.extend(["", "", ""])
            table_data.append(train_schedule)
            isFirstStation = False

    table = Table(table_data)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.white),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                               ('FONTSIZE', (0, 0), (-1, -1), 8),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    doc.build([table])

def trains_timings_linear_to_pdf(problem):
    """
    Function to print problem linear timetable to a PDF file
    """
    output_file = "train_schedule_linear.pdf"
    prob, optimization_time = solveLinearProblem(problem)

    if os.path.exists(output_file):
        os.remove(output_file)

    doc = SimpleDocTemplate(output_file, pagesize=letter)
    
    header_row = ["Traukinys", "Stotis", "Atvykimo laikas", "Išvykimo laikas", "Stotis", "Atvykimo laikas", "Išvykimo laikas"]
    table_data = [header_row]

    for train_id in problem.trains_routes["T"]:
        isFirstStation = True
        route = problem.trains_routes["Routes"][train_id]
        for i in range(0, len(route), 2): 
            station1 = route[i]
            station2 = route[i + 1] if i + 1 < len(route) else None
            train_schedule = [train_id]
            departure_info1 = getDepartureArrivalInfoForPdf(problem.trains_routes, problem.trains_timing, prob, train_id, station1, isFirstStation)
            train_schedule.append(station1)
            train_schedule.append(departure_info1["conflict_free_arrival_time"])
            train_schedule.append(departure_info1["conflict_free_departure_time"])
            if station2:
                departure_info2 = getDepartureArrivalInfoForPdf(problem.trains_routes, problem.trains_timing, prob, train_id, station2, isFirstStation)
                train_schedule.append(station2)
                train_schedule.append(departure_info2["conflict_free_arrival_time"])
                train_schedule.append(departure_info2["conflict_free_departure_time"])
            else:
                train_schedule.extend(["", "", ""])
            table_data.append(train_schedule)
            isFirstStation = False

    table = Table(table_data)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.white),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                               ('FONTSIZE', (0, 0), (-1, -1), 8),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    doc.build([table])

def trains_timings_simulated_to_pdf(problem, problem_file):
    """
    Function to print problem simulated quantum timetable to a PDF file
    """
    output_file = "train_schedule_simulated.pdf"

    Q = np.load(problem_file)["Q"]
    f = f"files/QUBO_complete_sol_sim-anneal"
    solutions, energies, occurrences = load_train_solution(f, 0)

    trains_routes = problem.trains_routes
    trains_trains_timing = problem.trains_timing
    inds, q_bits = indexingForQubo(trains_routes,trains_trains_timing, problem.d_max)

    if os.path.exists(output_file):
        os.remove(output_file)

    doc = SimpleDocTemplate(output_file, pagesize=letter)
    
    header_row = ["Traukinys", "Stotis", "Atvykimo laikas", "Išvykimo laikas", "Stotis", "Atvykimo laikas", "Išvykimo laikas"]
    table_data = [header_row]

    current_train_id = inds[0]["t"]
    current_train_schedule = None

    row = 1
    for i in range(q_bits):
        if solutions[0][i] == 1:
            t = inds[i]["t"]
            s = inds[i]["s"]
            d = inds[i]["d"]
            a = inds[i]["a"]
            time = d + earliestDepartureTime(trains_routes["Routes"], problem.trains_timing, t, s)
            if (t == current_train_id):
                if (row == 2):
                    current_train_id = t
                    current_train_schedule.append(s) 
                    current_train_schedule.append(toHoursMinutes(int(time)-int(a)))
                    current_train_schedule.append(toHoursMinutes(int(time)))
                    table_data.append(current_train_schedule)
                    row = 1
                else:
                    current_train_id = t
                    current_train_schedule = [t]
                    current_train_schedule.append(s) 
                    current_train_schedule.append(toHoursMinutes(int(time)-int(a)))
                    current_train_schedule.append(toHoursMinutes(int(time)))
                    row = row + 1
            else:
                if (row == 2):
                    current_train_schedule.append("") 
                    current_train_schedule.append("")
                    current_train_schedule.append("") 
                    table_data.append(current_train_schedule)
                    current_train_id = t
                    current_train_schedule = [t]
                    current_train_schedule.append(s) 
                    current_train_schedule.append(toHoursMinutes(int(time)-int(a)))
                    current_train_schedule.append(toHoursMinutes(int(time)))
                    table_data.append(current_train_schedule)
                    row = 1
                else:
                    current_train_id = t
                    current_train_schedule = [t]
                    current_train_schedule.append(s) 
                    current_train_schedule.append("")
                    current_train_schedule.append(toHoursMinutes(int(time)))
                    row = row + 1 
                
    
    table = Table(table_data)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.white),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                               ('FONTSIZE', (0, 0), (-1, -1), 8),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    doc.build([table])