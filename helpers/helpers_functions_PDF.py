"""
Helpers for PDF formating
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

from encoders.ILP_encoder import solveLinearProblem, getDepartureArrivalInfoForPdf, toHoursMinutes
from encoders.QUBO_encoder import edt, indexingForQubo
from helpers.helpers_functions_QUBO import load_train_solution
from helpers.helpers_functions import toDateTime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle


def trains_timings_to_pdf(problem, problem_file, problem_number):
    trains_timings_orginal_to_pdf(problem, problem_number)
    trains_timings_linear_to_pdf(problem, problem_number)
    trains_timings_simulated_to_pdf(problem, problem_file, problem_number)

def trains_timings_to_png(problem, problem_file, problem_number):
    trains_timings_orginal_to_png(problem, problem_number)
    trains_timings_linear_to_png(problem, problem_number)
    trains_timings_simulated_to_png(problem, problem_file, problem_number)
    trains_timings_quantum_to_png(problem, problem_file, problem_number)

def trains_timings_orginal_to_png(problem, problem_number):
    """
    Function to print problem original timetable to a PNG file
    """
    output_file = f"files/solutions/original/train_schedule_original{problem_number}.png"
    prob = solveLinearProblem(problem)

    if os.path.exists(output_file):
        os.remove(output_file)

    stations = []
    trains = {} 

    for train_id in problem.trains_routes["T"]:
        isFirstStation = True
        route = problem.trains_routes["Routes"][train_id]
        for i in range(0, len(route), 1): 
            station = route[i]
            departure_info = getDepartureArrivalInfoForPdf(problem.trains_routes, problem.trains_timing, prob, train_id, station, isFirstStation)
            if station not in stations:
                stations.append(station)
            if train_id not in trains:
                trains[train_id] = {"stations": [], "times": []}
                
            trains[train_id]["stations"].extend([station, station])
            trains[train_id]["times"].extend([departure_info["conflicted_arrival_time"], departure_info["conflicted_departure_time"]])
            isFirstStation = False
    
    plt.xlabel('Laikas')
    plt.ylabel('Stotis')
    plt.title('Originalus tvarkaraštis')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=15))

    for train_id, data in sorted(trains.items(), key=lambda x: min(x[1]["times"])):
        plt.plot(data["times"], data["stations"], label=f'Traukinys {train_id}', linewidth=2)

    min_time = min(min(t["times"]) for t in trains.values())
    max_time = max(max(t["times"]) for t in trains.values())
    plt.xlim(min_time, max_time)
    
    plt.xticks(rotation=45, fontsize=7)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def trains_timings_linear_to_png(problem, problem_number):
    """
    Function to print problem linear timetable to a PNG file
    """
    output_file = f"files/solutions/linear/train_schedule_linear{problem_number}.png"
    prob = solveLinearProblem(problem)

    if os.path.exists(output_file):
        os.remove(output_file)

    stations = []
    trains = {} 

    for train_id in problem.trains_routes["T"]:
        isFirstStation = True
        route = problem.trains_routes["Routes"][train_id]
        for i in range(0, len(route), 1): 
            station = route[i]
            departure_info = getDepartureArrivalInfoForPdf(problem.trains_routes, problem.trains_timing, prob, train_id, station, isFirstStation)
            if station not in stations:
                stations.append(station)
            if train_id not in trains:
                trains[train_id] = {"stations": [], "times": []}
                
            trains[train_id]["stations"].extend([station, station])
            trains[train_id]["times"].extend([departure_info["conflict_free_arrival_time"], departure_info["conflict_free_departure_time"]])
            isFirstStation = False
    
    plt.figure()
    plt.xlabel('Laikas')
    plt.ylabel('Stotis')
    plt.title('Perplanuotas tvarkaraštis naudojant PuLP')

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=15))

    for train_id, data in sorted(trains.items(), key=lambda x: min(x[1]["times"])):
        plt.plot(data["times"], data["stations"], label=f'Traukinys {train_id}', linewidth=2)

    min_time = min(min(t["times"]) for t in trains.values())
    max_time = max(max(t["times"]) for t in trains.values())
    plt.xlim(min_time, max_time)
    plt.xticks(rotation=45, fontsize=7)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def trains_timings_quantum_to_png(problem, problem_file, problem_number):
    """
    Function to print problem linear timetable to a PNG file
    """
    for i in [3,3.5,4,4.5]:
        f = f"files/dwave_data/QUBO_complete_sol_real_anneal_problem{problem_number}_numread2000_antime240_chainst{i}"
        solutions = load_train_solution(f, i)
        trains_routes = problem.trains_routes
        trains_trains_timing = problem.trains_timing
        inds, q_bits = indexingForQubo(trains_routes,trains_trains_timing, problem.d_max)

        output_file = f"files/solutions/quantum/train_schedule_quantum_problem{problem_number}_{i}.png"

        if os.path.exists(output_file):
            os.remove(output_file)

        stations = []
        trains = {} 
        for i in range(q_bits):
            if solutions[0][i] == 1:
                t = inds[i]["t"]
                s = inds[i]["s"]
                d = inds[i]["d"]
                a = inds[i]["a"]
                time = d + edt(trains_routes["Routes"], problem.trains_timing, t, s)

                if s not in stations:
                    stations.append(s)
                if t not in trains:
                    trains[t] = {"stations": [], "times": []}
                    
                trains[t]["stations"].extend([s, s])
                trains[t]["times"].extend([toDateTime(int(time)-int(a)), toDateTime(int(time))])
                plt.figure()
                plt.xlabel('Laikas')
                plt.ylabel('Stotis')
                plt.title('Perplanuotas tvarkaraštis naudojant D-Wave')

                plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=15))

                for train_id, data in sorted(trains.items(), key=lambda x: min(x[1]["times"])):
                    plt.plot(data["times"], data["stations"], label=f'Traukinys {train_id}', linewidth=2)

                min_time = min(min(t["times"]) for t in trains.values())
                max_time = max(max(t["times"]) for t in trains.values())
                plt.xlim(min_time, max_time)
                plt.xticks(rotation=45, fontsize=7)
                plt.legend()
                plt.tight_layout()
                plt.savefig(output_file)
                plt.close()

def trains_timings_simulated_to_png(problem, problem_file, problem_number):
    """
    Function to print problem simulated d-wave timetable to a PNG file
    """
    output_file = f"files/solutions/simulated/train_schedule_simulated{problem_number}.png"

    Q = np.load(problem_file)["Q"]
    f = f"files/QUBO_complete_sol_sim_anneal{problem_number}"
    solutions, energies, occurrences = load_train_solution(f, 0)

    trains_routes = problem.trains_routes
    trains_trains_timing = problem.trains_timing
    inds, q_bits = indexingForQubo(trains_routes,trains_trains_timing, problem.d_max)

    if os.path.exists(output_file):
        os.remove(output_file)

    stations = []
    trains = {} 

    for i in range(q_bits):
        if solutions[0][i] == 1:
            t = inds[i]["t"]
            s = inds[i]["s"]
            d = inds[i]["d"]
            a = inds[i]["a"]
            time = d + edt(trains_routes["Routes"], problem.trains_timing, t, s)

            if s not in stations:
                stations.append(s)
            if t not in trains:
                trains[t] = {"stations": [], "times": []}
                    
            trains[t]["stations"].extend([s, s])
            trains[t]["times"].extend([toDateTime(int(time)-int(a)), toDateTime(int(time))])
        
    plt.figure()
    plt.xlabel('Laikas')
    plt.ylabel('Stotis')
    plt.title('Perplanuotas tvarkaraštis naudojant D-Wave simuliatoriu')

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=15))

    for train_id, data in sorted(trains.items(), key=lambda x: min(x[1]["times"])):
        plt.plot(data["times"], data["stations"], label=f'Traukinys {train_id}', linewidth=2)

    min_time = min(min(t["times"]) for t in trains.values())
    max_time = max(max(t["times"]) for t in trains.values())
    plt.xlim(min_time, max_time)
    plt.xticks(rotation=45, fontsize=7)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def trains_timings_orginal_to_pdf(problem, problem_number):
    """
    Function to print problem original timetable to a PDF file
    """
    output_file = f"files/solutions/original/train_schedule_original{problem_number}.pdf"
    prob = solveLinearProblem(problem)

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
            train_schedule.append(departure_info1["conflicted_arrival_time"].time())
            train_schedule.append(departure_info1["conflicted_departure_time"].time())
            if station2:
                departure_info2 = getDepartureArrivalInfoForPdf(problem.trains_routes, problem.trains_timing, prob, train_id, station2, isFirstStation)
                train_schedule.append(station2)
                train_schedule.append(departure_info2["conflicted_arrival_time"].time())
                train_schedule.append(departure_info2["conflicted_departure_time"].time())
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

def trains_timings_linear_to_pdf(problem, problem_number):
    """
    Function to print problem linear timetable to a PDF file
    """
    output_file = f"files/solutions/linear/train_schedule_linear{problem_number}.pdf"
    prob = solveLinearProblem(problem)

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
            train_schedule.append(departure_info1["conflict_free_arrival_time"].time())
            train_schedule.append(departure_info1["conflict_free_departure_time"].time())
            if station2:
                departure_info2 = getDepartureArrivalInfoForPdf(problem.trains_routes, problem.trains_timing, prob, train_id, station2, isFirstStation)
                train_schedule.append(station2)
                train_schedule.append(departure_info2["conflict_free_arrival_time"].time())
                train_schedule.append(departure_info2["conflict_free_departure_time"].time())
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

def trains_timings_simulated_to_pdf(problem, problem_file, problem_number):
    """
    Function to print problem simulated quantum timetable to a PDF file
    """
    output_file = f"files/solutions/simulated/train_schedule_simulated{problem_number}.pdf"

    Q = np.load(problem_file)["Q"]
    f = f"files/QUBO_complete_sol_sim_anneal{problem_number}"
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
            time = d + edt(trains_routes["Routes"], problem.trains_timing, t, s)
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