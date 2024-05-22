""" 
Encoder for ILP/MPL solver
"""
import itertools
import pulp as pus

from helpers.helpers_functions_QUBO  import departureStationForSwitches, earliestDepartureTime, tau, previousStation, occursAsPair
from helpers.helpers_functions_ILP import canMO, trainsEnteringViaSameSwitches, getM, updateDictOfDicts
from helpers.helpers_functions import toDateTime

def orderVariables(train_sets):
    """
    Function that returns ordered variables in pus.LpVariable.dicts for constrains
    """
    order_vars = {}
    orderForSingleLineConstrain(order_vars, train_sets)
    orderForMinimalSpanConstrain(order_vars, train_sets)
    orderForTrackOccupationAtStations(order_vars, train_sets)
    orderForSwitchOccupation(order_vars, train_sets)
    return order_vars

def orderForSingleLineConstrain(order_vars, train_sets):
    """
    Function that adds to nested order_vars dict order variables for single line constrains
    """
    for s in train_sets["T0"].keys():
        for (t, tp) in train_sets["T0"][s]:
            updateBetween2Trains2Stations(order_vars, t, tp, s[0], s[1])

def orderForMinimalSpanConstrain(order_vars, train_sets):
    """
    Function that adds to nested order_vars dict order variables for minimal span constrains
    """
    for s in train_sets["T1"].keys():
        for all_ts in train_sets["T1"][s].values():
            for ts in all_ts:
                for (t, tp) in itertools.combinations(ts, 2):
                    updateBetween2Trains1Station(order_vars, str(t), str(tp), str(s))

def orderForTrackOccupationAtStations(order_vars, train_sets):
    """
    Function that adds to nested order_vars dict order variables for track occupation constrains
    """
    for s in train_sets["Ttrack"].keys():
        for ts in train_sets["Ttrack"][s]:
            for (t, tp) in itertools.combinations(ts, 2):
                updateBetween2Trains1Station(order_vars, str(t), str(tp), str(s))

def orderForSwitchOccupation(order_vars, train_sets):
    """
    Function that adds to nested order_vars dict order variables for track occupation
    """
    for s in train_sets["Tswitch"].keys():
        for pair in train_sets["Tswitch"][s]:
            for (tp, tpp) in itertools.combinations(pair.keys(), 2):
                sp = departureStationForSwitches(s, tp, pair, train_sets)
                spp = departureStationForSwitches(s, tpp, pair, train_sets)
                if sp == spp:
                    if (sp != s and canMO(tp, tpp, s, train_sets)):
                        updateY4In(order_vars, "in", tp, tpp, s)
                    else:
                        updateBetween2Trains1Station(order_vars, str(tp), str(tpp), str(sp))
                elif s in (sp, spp):
                    updateBetween2Trains2Stations(order_vars, tp, tpp, sp, spp)
                else: # we have differen s, sp and spp
                    updateY4In(order_vars, "in", tp, tpp, s)

def updateBetween2Trains1Station(order_var, t, tp, s):
    """
    Function to make varaible for 2 trains and 1 station
    """
    check1 = checkOrderFor2Train1Station(order_var, t, tp, s)
    check2 = checkOrderFor2Train1Station(order_var, tp, t, s)
    if not (check1 or check2):
        # 3 as there are 3 vars
        y = pus.LpVariable.dicts("y", ([t], [tp], ["one_station"], [s]), 0, 1, cat="Integer")
        updateDictOfDicts(order_var, y)

def updateBetween2Trains2Stations(order_var, t, tp, s, sp):
    """
    Function to make varaible for 2 trains and 2 station
    """
    check1 = checkOrderVar2Train2Stations(order_var, t, tp, s, sp)
    check2 = checkOrderVar2Train2Stations(order_var, tp, t, sp, s)
    if not (check1 or check2):
        z = pus.LpVariable.dicts("z", ([t], [tp], [s], [sp]), 0, 1, cat="Integer")
        updateDictOfDicts(order_var, z)

def updateY4In(order_var, a, t, tp, s):
    """
    Function that checks if there is an order variable for (a,j,jp,s) or for (a,jp,j,s)
    """
    check1 = checkOrderVar2Train2Stations(order_var, a, t, tp, s)
    check2 = checkOrderVar2Train2Stations(order_var, a, tp, t, s)
    if not (check1 or check2):
        z = pus.LpVariable.dicts("z", ([a], [t], [tp], [s]), 0, 1, cat="Integer")
        updateDictOfDicts(order_var, z)

def getOrder2Train1Station(order_var, t, tp, s):
    """
    Gets order variable for two trains (t,tp) and one station (s)
    """
    if checkOrderFor2Train1Station(order_var, t, tp, s):
        return order_var[t][tp]["one_station"][s]
    return 1 - order_var[tp][t]["one_station"][s]

def getOrder2Train2Stations(y, t, tp, s, sp):
    """
    Function that gets order variable for two trains (t,tp) and two stations (s, sp)
    """
    if checkOrderVar2Train2Stations(y, t, tp, s, sp):
        return y[t][tp][s][sp]
    return 1 - y[tp][t][sp][s]

def getY4In(y, a, t, tp, s):
    """
    Funnction as get_y4_singleline but permutes only t and tp
    """
    if checkOrderVar2Train2Stations(y, a, t, tp, s):
        return y[a][t][tp][s]
    return 1 - y[a][tp][t][s]

def checkOrderFor2Train1Station(y, t, tp, s):
    """
    Function to checks if in y there is an order variable for 2 trains and 1 station
    """
    return t in y and tp in y[t] and "one_station" in y[t][tp] and s in y[t][tp]["one_station"]

def checkOrderVar2Train2Stations(y, t, tp, s, sp):
    """
    Function that checks if in y there is an order variable for 2 train 2 stations
    """
    return t in y and tp in y[t] and s in y[t][tp] and sp in y[t][tp][s]

def delayVariables(train_sets, d_max, cat):
    """
    Function to return all delay variables
    """
    secondary_delays_vars = {}
    for t in train_sets["T"]:
        for s in train_sets["Routes"][t]:
            dvar = pus.LpVariable.dicts("Delays", ([t], [s]), 0, d_max, cat=cat)
            updateDictOfDicts(secondary_delays_vars, dvar)

    return secondary_delays_vars

def minimalSpanConstrain(s, sp, t, tp, problem, timetable, delay_var, y, train_sets, d_max):
    """
    Function to ecnode constrains for minimal span condition
    """
    S = train_sets["Routes"]
    LHS = earliestDepartureTime(S, timetable, tp, s)
    RHS = earliestDepartureTime(S, timetable, t, s)
    RHS += tau(timetable, "t_headway", first_train=t, second_train=tp, first_station=s, second_station=sp)
    M = getM(LHS, RHS, d_max)

    if LHS - d_max < RHS:  # otherwise always fulfilled  (redundant)
        LHS += delay_var[tp][s]
        RHS += delay_var[t][s]
        RHS -= M * getOrder2Train1Station(y, str(tp), str(t), str(s))
        problem += LHS >= RHS, f"minimal_span_{tp}_{t}_{s}_{sp}"

def minimalSpan(problem, timetable, delay_var, y, train_sets, d_max):
    """
    Function to add the minimum span condition to the pulp problem
    """
    for s in train_sets["T1"].keys():
        for sp in train_sets["T1"][s].keys():
            for js in train_sets["T1"][s][sp]:
                for (j, jp) in itertools.combinations(js, 2):
                    minimalSpanConstrain(s, sp, j, jp, problem, timetable, delay_var, y, train_sets, d_max)
                    minimalSpanConstrain(s, sp, jp, j, problem, timetable, delay_var, y, train_sets, d_max)

def singleLineConstrain(s, sp, t, tp, problem, timetable, delay_var, y, train_sets, d_max):
    """
    Function to encode constsains for the single line condition
    """
    S = train_sets["Routes"]
    LHS = earliestDepartureTime(S, timetable, t, s)
    RHS = earliestDepartureTime(S, timetable, tp, sp)
    RHS += tau(timetable, "t_pass", first_train=tp, first_station=sp, second_station=s)
    M = getM(LHS, RHS, d_max)

    if LHS - d_max < RHS:  # otherwise always fulfilled (redundant)
        LHS += delay_var[t][s]
        RHS += delay_var[tp][sp]
        RHS -= M * getOrder2Train2Stations(y, t, tp, s, sp)
        problem += LHS >= RHS, f"single_line_{t}_{tp}_{s}_{sp}"

def singleLine(problem, timetable, delay_var, y, train_sets, d_max):
    """
    Function to add single line condition to the pulp problem
    """
    for (s, sp) in train_sets["T0"].keys():
        if (s, sp) in train_sets["T0"]:
            for (t, tp) in train_sets["T0"][(s, sp)]:
                singleLineConstrain(s, sp, t, tp, problem, timetable, delay_var, y, train_sets, d_max)
                singleLineConstrain(sp, s, tp, t, problem, timetable, delay_var, y, train_sets, d_max)

def minimalStayConstrain(t, s, problem, timetable, delay_var, train_sets):
    """
    Function to encode constrains for minimal stay condition
    """
    S = train_sets["Routes"]
    sp = previousStation(S[t], s)
    if sp is not None:
        if s in delay_var[t]: 
            LHS = delay_var[t][s]
            LHS += earliestDepartureTime(S, timetable, t, s)
            RHS = delay_var[t][sp]
            RHS += earliestDepartureTime(S, timetable, t, sp)
            RHS += tau(timetable, "t_pass", first_train=t, first_station=sp, second_station=s)
            RHS += tau(timetable, "t_stop", first_train=t, first_station=s)
            problem += (LHS >= RHS, f"minimal_stay_{t}_{s}")

def minimalStay(problem, timetable, delay_var, train_sets):
    """
    Function to add minimal stay on the staiton to the pulp problem
    """
    for t in train_sets["T"]:
        for s in train_sets["Routes"][t]:
            minimalStayConstrain(t, s, problem, timetable, delay_var, train_sets)

def keepTrainsOrder(s, t, tp, problem, y, train_sets):
    """
    Helper function for single track occupation at the station constrain
    """
    S = train_sets["Routes"]
    # Assuming previousStation is a function defined elsewhere
    sp = previousStation(S[str(t)], s)

    if sp in train_sets["T0"].keys():
        if s in train_sets["T0"][sp].keys():
            # if both trains goes sp -> s and have common path
            if occursAsPair(t, tp, train_sets["Ttrack"][s]):
                if not canMO(t, tp, s, train_sets):
                    # the order on station y[j][jp][s] must be the same as
                    # on the path y[j][jp][sp] (previous station)
                    if s in y[t][tp]["one_station"] and sp in y[t][tp]["one_station"]:
                        problem += (y[t][tp]["one_station"][s] == y[t][tp]["one_station"][sp], f"track_occupation_{t}_{tp}_{s}_{sp}")
                elif trainsEnteringViaSameSwitches(train_sets, s, t, tp):
                    problem += (getY4In(y, "in", t, tp, s) == y[t][tp]["one_station"][s], f"track_occupation_{t}_{tp}_{s}_{sp}")

def trainsOrderAtStation(s, t, tp, problem, timetable, delay_var, y, train_sets, d_max):
    """
    Helper function for track occupation condition
    """
    S = train_sets["Routes"]

    sp = previousStation(S[str(tp)], s)
    if sp is not None:
        LHS = earliestDepartureTime(S, timetable, tp, sp)
        LHS += tau(timetable, "t_pass", first_train=tp, first_station=sp, second_station=s)
    else: 
        LHS = earliestDepartureTime(S, timetable, tp, s)

    RHS = earliestDepartureTime(S, timetable, t, s)
    M = getM(LHS, RHS, d_max)

    if LHS - d_max < RHS:
        if sp is not None:
            LHS += delay_var[str(tp)][sp]

        RHS -= M * getOrder2Train1Station(y, str(tp), str(t), str(s))
        LHS -= delay_var[str(t)][s]

        problem += LHS >= RHS, f"track_occupation_{t}_{tp}_{s}_p"

def trackOccupation(problem, timetable, delay_var, y, train_sets, d_max):
    """
    Function to add track occupation condition to the pulp problem
    """
    for s in train_sets["Ttrack"].keys():
        for js in train_sets["Ttrack"][s]:
            js = [int(num) for num in js]
            for (j, jp) in itertools.combinations(js, 2):
                keepTrainsOrder(s, str(j), str(jp), problem, y, train_sets)
                trainsOrderAtStation(s, jp, j, problem, timetable, delay_var, y, train_sets, d_max)
                trainsOrderAtStation(s, j, jp, problem, timetable, delay_var, y, train_sets, d_max)

def switchOcc(s, tp, sp, tpp, spp, problem, timetable, delay_var, y, train_sets, d_max):
    """
    Helper function for switchOccupation
    """
    S = train_sets["Routes"]
    LHS = earliestDepartureTime(S, timetable, tp, sp)
    RHS = earliestDepartureTime(S, timetable, tpp, spp)
    RHS += tau(timetable, "res", first_train=tp, second_train=tpp, first_station=s)

    if s != sp:
        LHS += tau(timetable, "t_pass", first_train=tp, first_station=sp, second_station=s)

    if s != spp:
        RHS += tau(timetable, "t_pass", first_train=tpp, first_station=spp, second_station=s)

    M = getM(LHS, RHS, d_max)

    if LHS < RHS + d_max:
        if spp == sp:
            if sp != s and canMO(tp, tpp, s, train_sets):
                RHS -= M * getY4In(y, "in", tp, tpp, s)
            else:
                RHS -= M * getOrder2Train1Station(y, str(tp), str(tpp), str(sp))
        elif s in (spp, sp):
            RHS -= M * getOrder2Train2Stations(y, tp, tpp, sp, spp)
        else: # s, sp and spp differs
            RHS -= M * getY4In(y, "in", tp, tpp, s)

        LHS += delay_var[tp][sp]
        RHS += delay_var[tpp][spp]

        problem += LHS >= RHS, f"switch_{tp}_{tpp}_{s}_{sp}_{spp}"

def switchOccupation(problem, timetable, delay_var, y, train_sets, d_max):
    """
    Function that adds switch occupation condition to the pulp problem
    """
    for s in train_sets["Tswitch"].keys():
        for pair in train_sets["Tswitch"][s]:
            for (tp, tpp) in itertools.combinations(pair.keys(), 2):
                tp = str(tp)
                tpp = str(tpp)
                sp = departureStationForSwitches(s, tp, pair, train_sets)
                spp = departureStationForSwitches(s, tpp, pair, train_sets)
                if (sp and spp is not None):
                    switchOcc(s, tp, sp, tpp, spp, problem, timetable, delay_var, y, train_sets, d_max)
                    switchOcc(s, tpp, spp, tp, sp, problem, timetable, delay_var, y, train_sets, d_max)

def objective(problem, timetable, delay_var, train_sets, d_max):
    """S
    Function to add objective function to the pulp problem
    """
    S = train_sets["Routes"]
    problem += pus.lpSum(
        [
            delay_var[i][j] * 0 / d_max
            for i in train_sets["T"]
            for j in S[i]
        ])

def createLinearProblem(problem, cat):
    """
    Function to create the linear problem model
    """
    train_sets = problem.trains_routes
    timetable = problem.trains_timing
    d_max = problem.d_max
    prob = pus.LpProblem("Trains", pus.LpMinimize)
    secondary_delays_var = delayVariables(train_sets, d_max, cat = cat)
    y = orderVariables(train_sets)

    minimalSpan(prob, timetable, secondary_delays_var, y, train_sets, d_max)
    minimalStay(prob, timetable, secondary_delays_var, train_sets)
    singleLine(prob, timetable, secondary_delays_var, y, train_sets, d_max)
    trackOccupation(prob, timetable, secondary_delays_var, y, train_sets, d_max)
    switchOccupation(prob, timetable, secondary_delays_var, y, train_sets, d_max)

    objective(prob, timetable, secondary_delays_var, train_sets, d_max)

    return prob

def solveLinearProblem(problem, cat = "Integer"):
    """
    Function which solves the linear problem returns the pulp object
    """
    prob = createLinearProblem(problem, cat)
    prob.solve(pus.PULP_CBC_CMD(msg=False))

    return prob

def printDeparture(train_sets, timetable, prob, t, s, data = []):
    """
    Function to return confict free and conflicted time
    """
    for v in prob.variables():
        if v.name == f"Delays_{t}_{s}":
            if data == []:
                delay = v.varValue
            else:
                delay = data[v.name]

            conflicted_tt = earliestDepartureTime(train_sets["Routes"], timetable, t, s)
            conflict_free = delay + conflicted_tt
            print("Train", t, "goes from station", s, "(dep. time)", toHoursMinutes(int(conflict_free)), " with ", int(delay), " minutes delay (original time",toHoursMinutes(int(conflicted_tt)),")")

def getDepartureArrivalInfoForPdf(train_sets, timetable, prob, t, s, isFirstStation, data = []):
    """
    Function to return confict free and conflicted time
    """
    delay = 0
    for v in prob.variables():
        if v.name == f"Delays_{t}_{s}":
            if data == []:
                delay = v.varValue
            else:
                delay = data[v.name]
  
    conflicted_departure_tt = earliestDepartureTime(train_sets["Routes"], timetable, t, s)
    conflict_free_departure = delay + conflicted_departure_tt

    conflicted_stop_at_station = conflict_free_departure
    stop_at_station = int(conflicted_departure_tt)
    if (isFirstStation == False):
        stop_at_station = int(conflicted_departure_tt) - int(tau(timetable, "t_stop", t, s))
        conflicted_stop_at_station = conflict_free_departure - int(tau(timetable, "t_stop", t, s))

    departure_info = {
        "train_number": t,
        "station": s,
        "conflict_free_departure_time": toDateTime(int(conflict_free_departure)),
        "conflict_free_arrival_time": toDateTime(int(conflicted_stop_at_station)),
        "delay": int(delay),
        "conflicted_departure_time": toDateTime(int(conflicted_departure_tt)),
        "conflicted_arrival_time": toDateTime(int(stop_at_station))
    }

    return departure_info

def toHoursMinutes(minutes):
    hours = minutes // 60
    min = minutes % 60
    return f"{hours:02d}:{min:02d}"

def impact_to_objective(prob, timetable, t, s, d_max, data = []):
    """
    Function to calculate impact to the objective of the particular secondary delay of particular train at particular station
    """
    for v in prob.variables():
        if v.name == f"Delays_{t}_{s}":
            if data == []:
                delay = v.varValue
            else:
                delay = data[v.name]
            return 0 / d_max * delay
    return 0.0