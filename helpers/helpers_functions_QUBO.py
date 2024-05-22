"""
Helpers for QUBO creation 
"""
import numpy as np
import pickle as pk
import numpy as np
import dimod

def occursAsPair(a, b, vecofvec):
    """
    Function checks whether a and b occurs together in the same vector of vectors 
    """
    for v in vecofvec:
        if a in v and b in v and a != b:
            return True
    return False

def subsequentStation(route, s):
    """
    Function to return next station in route
    """
    k = route.index(s)
    if k == len(route) - 1:
        return None
    return route[k + 1]

def previousStation(route, s):
    """
    Function to return preceeding station in the route
    """
    k = route.index(s)
    if k == 0:
        return None
    return route[k - 1]

def tau(trains_timing, key, first_train=None, first_station=None, second_station=None, second_train=None):
    """
    Function that returns particular time span τ(key) for given train and station or stations
    """
    if key == "t_headway":
        return trains_timing["tau"]["t_headway"][
            f"{first_train}_{second_train}_{first_station}_{second_station}"
        ]
    if key == "t_pass":
        string = f"{first_train}_{first_station}_{second_station}"
        return trains_timing["tau"][key][string]
    if key == "t_stop":
        return trains_timing["tau"][key][f"{first_train}_{first_station}"]
    if key == "t_prep":
        return trains_timing["tau"][key][f"{first_train}_{first_station}"]
    if key == "res":
        return trains_timing["tau"]["res"]
    return -1000

def earliestDepartureTime(S, trains_timing, train, station):
    """
    Fuction that returns earliest possible departure of a train from the given station
    """
    if "schedule" in trains_timing:
        sched = trains_timing["schedule"][f"{train}_{station}"]
    else:
        sched = -np.inf
    train_station = f"{train}_{station}"

    if train_station in trains_timing["t_out"]:
        unaviodable = trains_timing["t_out"][train_station]
        return np.maximum(sched, unaviodable)

    s = previousStation(S[str(train)], station)
        
    tau_pass = tau(
        trains_timing,
        "t_pass",
        first_train=train,
        first_station=s,
        second_station=station,
    )
    tau_stop = tau(trains_timing, "t_stop", first_train=train, first_station=station)
    unavoidable = earliestDepartureTime(S, trains_timing, train, s) + tau_pass
    unavoidable += tau_stop

    return np.maximum(sched, unavoidable)

def load_train_solution(f, i):
    """
    Function to load particular DWave solution from file
    """
    file = open(
        f, 'rb')

    output = pk.load(file)
    sampleset =  dimod.SampleSet.from_serializable(output)

    sorted = np.sort(sampleset.record, order="energy")
    solutions = [sol[0] for sol in sorted]

    return solutions

def departureStationForSwitches(s, j, place_of_switch, trains_routes):
    """
    Function that returns the station symbol from which train t departs prior to passing the switch at station s
    """
    if place_of_switch[j] == "out":
        return s
    if place_of_switch[j] == "in":
        S = trains_routes["Routes"]
        return previousStation(S[j], s)
    return 0

def energy(v, Q):
    """
    Function to compute energy from QUBO
    """
    if -1 in v:
        v = [(y + 1) / 2 for y in v]
    X = np.array(Q)
    V = np.array(v)

    return V @ X @ V.transpose()
