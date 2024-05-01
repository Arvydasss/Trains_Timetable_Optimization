"""
Encodes problem to QUBO
"""
import itertools
import numpy as np
from helpers.helpers_functions_QUBO import penaltyWeights, subsequentStation, occursAsPair, earliestDepartureTime, tau, departureStationForSwitches

def indexingForQubo(trains_routes, trains_timing, d_max):
    """
    Function to return vector of dicts of trains stations, delays and stop at the station {"j": j, "s": s, "d": d, "a": a}
    """
    S = trains_routes["Routes"]
    T_stop = trains_timing["tau"]["t_stop"]
    inds = []
    for j in trains_routes["T"]:
        for s in S[j]:
            for d in range(d_max + 1):
                a_value = T_stop.get(j+'_'+s, 0)
                inds.append({"t": j, "s": s, "d": d, "a": a_value})
    return inds, len(inds)

def pSum(k, l, jsd_dicts):
    """
    Function for sum to one conditon
    """
    if jsd_dicts[k]["t"] == jsd_dicts[l]["t"] and jsd_dicts[k]["s"] == jsd_dicts[l]["s"]:
        if jsd_dicts[k]["d"] == jsd_dicts[l]["d"]:
            return -1.0
        return 1.0
    return 0.0


def pHeadway(k, l, jsd_dicts, trains_timing, trains_routes):
    """
    Function for minimal headway condition
    """
    S = trains_routes["Routes"]
    t = jsd_dicts[k]["t"]
    t1 = jsd_dicts[l]["t"]
    s = jsd_dicts[k]["s"]
    s1 = jsd_dicts[l]["s"]
    s_next = subsequentStation(S[t], s)

    if s == s1 and s_next and s_next == subsequentStation(S[t1], s1):
        if s in trains_routes["T0"].keys():
            if s_next in trains_routes["T0"][s].keys():
                if occursAsPair(t, t1, trains_routes["T0"][s][s_next]):
                    time = jsd_dicts[k]["d"] + earliestDepartureTime(S, trains_timing, t, s)
                    time1 = jsd_dicts[l]["d"] + earliestDepartureTime(S, trains_timing, t1, s)

                    A = -tau(trains_timing, "t_headway", first_train=t1, second_train=t, first_station=s, second_station=s_next)
                    B = tau(trains_timing, "t_headway", first_train=t, second_train=t1, first_station=s, second_station=s_next)

                    if A < time1 - time < B:
                        return 1.0
    return 0.0

def pSingleTrack(k, l, jsd_dicts, trains_timing, trains_routes):
    """
    Function for single track line condition
    """
    p = penaltySingleTrack(k, l, jsd_dicts, trains_timing, trains_routes)
    p += penaltySingleTrack(l, k, jsd_dicts, trains_timing, trains_routes)
    return p

def penaltySingleTrack(k, l, jsd_dicts, trains_timing, trains_routes):
    """
    Helper function for pSingleTrack
    """
    S = trains_routes["Routes"]
    t = jsd_dicts[k]["t"]
    t1 = jsd_dicts[l]["t"]
    s = jsd_dicts[k]["s"]
    s1 = jsd_dicts[l]["s"]

    if (s, s1) in trains_routes["T0"].keys() and [t, t1] in trains_routes["T0"][(s, s1)]:
        time = jsd_dicts[k]["d"] + earliestDepartureTime(S, trains_timing, t, s)
        time2 = time
        time1 = jsd_dicts[l]["d"] + earliestDepartureTime(S, trains_timing, t1, s1)
        time -= tau(trains_timing, "t_pass", first_train=t1, first_station=s1, second_station=s)
        time2 += tau(trains_timing, "t_pass", first_train=t, first_station=s, second_station=s1)
        if time < time1 < time2:
            return 1.0
        
    return 0.0

def pMinimalStay(k, l, jsd_dicts, trains_timing, trains_routes):
    """
    Function for minimal stay condition
    """
    S = trains_routes["Routes"]
    p = penaltyMinimalStay(k, l, jsd_dicts, trains_timing, S)
    p += penaltyMinimalStay(l, k, jsd_dicts, trains_timing, S)
    return p

def penaltyMinimalStay(k, l, jsd_dicts, trains_timing, S):
    """
    Helper function for PMinimalStay
    """
    j = jsd_dicts[k]["t"]

    if j == jsd_dicts[l]["t"]:
        sp = jsd_dicts[k]["s"]
        s = jsd_dicts[l]["s"]
        if s == subsequentStation(S[j], sp):
            lhs = jsd_dicts[l]["d"]
            lhs += earliestDepartureTime(S, trains_timing, j, s)
            rhs = jsd_dicts[k]["d"]
            rhs += earliestDepartureTime(S, trains_timing, j, sp)
            rhs += tau(trains_timing, "t_pass", first_train=j, first_station=sp, second_station=s)
            rhs += tau(trains_timing, "t_stop", first_train=j, first_station=s)

            if lhs < rhs:
                return 1.0
    return 0.0

def pSwitchOccupation(k, l, inds, trains_timing, trains_routes):
    """
    Function for switch occupancy condition
    """
    S = trains_routes["Routes"]
    tp = inds[k]["t"]
    tpp = inds[l]["t"]
    sp = inds[k]["s"]
    spp = inds[l]["s"]

    for s in trains_routes["Tswitch"].keys():
        for pairs_of_switch in trains_routes["Tswitch"][s]:
            if [tp, tpp] == list(pairs_of_switch.keys()) or [tpp, tp] == list(pairs_of_switch.keys()):  # here is symmetrisation
                if sp == departureStationForSwitches(s, tp, pairs_of_switch, trains_routes):
                    if spp == departureStationForSwitches(s, tpp, pairs_of_switch, trains_routes):
                        t = inds[k]["d"] + earliestDepartureTime(S, trains_timing, tp, sp)
                        if s != sp:
                            t += tau(trains_timing, "t_pass", first_train=tp, first_station=sp, second_station=s)
                        t1 = inds[l]["d"] + earliestDepartureTime(S, trains_timing, tpp, spp)
                        if s != spp:
                            t1 += tau(trains_timing, "t_pass", first_train=tpp, first_station=spp, second_station=s)
                        p = penaltySwitch(t, t1, trains_timing)
                        if p > 0:
                            return p
    return 0.0

def penaltySwitch(t, t1, trains_timing):
    """
    Helper function for pSwitchOccupation
    """
    if -tau(trains_timing, "res") < t1 - t < tau(trains_timing, "res"):
        return 1.0
    return 0.0

##### track occupancy condition   - QUBO creation ####

def zIndices(trains_routes, d_max):
    """
    Auxiliary indexing for decomposition of qubic term,
    for track occupation condition

    Returns vector of dicts of 2 trains(j, j1) at delays(d, d1) at stations (s)

    {"j": j, "j1": j1, "s": s, "d": d, "d1": d1}
    """
    jsd_dicts = []
    for s in trains_routes["Ttrack"].keys():
        for js in trains_routes["Ttrack"][s]:
            for (j, j1) in itertools.combinations(js, 2):
                for d in range(d_max + 1):
                    for d1 in range(d_max + 1):
                        jsd_dicts.append({"t": j, "t1": j1, "s": s, "d": d, "d1": d1})
    return jsd_dicts, len(jsd_dicts)

def pTrackOccupationConditionQuadraticPart(k, l, jsd_dicts, trains_timing, trains_routes):
    """
    Function for quadratic part of track occupation condition
    """
    if len(jsd_dicts[k].keys()) == 3 and len(jsd_dicts[l].keys()) == 5:
        return pairOneTrackConstrains(jsd_dicts, k, l, trains_timing, trains_routes)

    if len(jsd_dicts[k].keys()) == 5 and len(jsd_dicts[l].keys()) == 3:
        return pairOneTrackConstrains(jsd_dicts, l, k, trains_timing, trains_routes)

    return 0.0

def pairOneTrackConstrains(jsd_dicts, k, l, trains_timing, trains_routes):
    """
    Helper function for pTrackOccupationConditionQuadraticPart
    """
    S = trains_routes["Routes"]
    tx = jsd_dicts[k]["t"]
    sx = jsd_dicts[k]["s"]
    sz = jsd_dicts[l]["s"]
    d = jsd_dicts[k]["d"]
    d1 = jsd_dicts[l]["d"]
    d2 = jsd_dicts[l]["d1"]

    if sz == subsequentStation(S[tx], sx):
        tz = jsd_dicts[l]["t"]
        tz1 = jsd_dicts[l]["t1"]

        if (tx == tz) and occursAsPair(tx, tz1, trains_routes["Ttrack"][sz]):
                # tz, tz1, tx => t', t, t''
                # sx, sz -> s', s
                p = oneTrackConstrains(tx, tz, tz1, sx, sz, d, d1, d2, trains_timing, trains_routes)
                if p > 0:
                    return p

        if (tx == tz1) and occursAsPair(tx, tz, trains_routes["Ttrack"][sz]):
                # tz1, tz, tx => t', t,  t''
                # sx, sz -> s', s
                p = oneTrackConstrains(tx, tz1, tz, sx, sz, d, d2, d1, trains_timing, trains_routes)
                if p > 0:
                    return p
    return 0

def oneTrackConstrains(jx, jz, jz1, sx, sz, d, d1, d2, trains_timing, trains_routes):
    """
    Helper function for pairOfOneTrackConstrains
    """
    S = trains_routes["Routes"]
    tx = d + earliestDepartureTime(S, trains_timing, jx, sx)
    tx += tau(trains_timing, "t_pass", first_train=jx, first_station=sx, second_station=sz)
    tz = d1 + earliestDepartureTime(S, trains_timing, jz, sz)
    tz1 = d2 + earliestDepartureTime(S, trains_timing, jz1, sz)

    if tx < tz1 <= tz:
        return 1.0
    return 0.0

def pRosenbergDecomposition(k, l, jsd_dicts, trains_routes):
    """
    Function for the contribution to from Rosenberg decomposition of qubic term

    Returns not weighted contribution to Qmat[k,l]=Qmat[l, k].
    Coificnets at k  ≠ l are divided by 2 because they are taken twice
    """
    S = trains_routes["Routes"]

    if len(jsd_dicts[k].keys()) == len(jsd_dicts[l].keys()) == 5:
        if k == l:
            return 3.0

    if len(jsd_dicts[k].keys()) == 3 and len(jsd_dicts[l].keys()) == 5:
        tx = jsd_dicts[k]["t"]
        sx = jsd_dicts[k]["s"]
        sz = jsd_dicts[l]["s"]
        if sz == sx:
            tz = jsd_dicts[l]["t"]
            tz1 = jsd_dicts[l]["t1"]

            # -1 because it is taken twice due to the symmetrisation
            if tx == tz:
                if jsd_dicts[k]["d"] == jsd_dicts[l]["d"]:
                    return -1.0
            if tx == tz1:
                if jsd_dicts[k]["d"] == jsd_dicts[l]["d1"]:
                    return -1.0

    # -1. 0 because it is taken twice due to the symmetrisation
    if len(jsd_dicts[k].keys()) == 5 and len(jsd_dicts[l].keys()) == 3:
        tx = jsd_dicts[l]["t"]
        sx = jsd_dicts[l]["s"]
        sz = jsd_dicts[k]["s"]
        if sz == sx:
            tz = jsd_dicts[k]["t"]
            tz1 = jsd_dicts[k]["t1"]
            if tx == tz:
                if jsd_dicts[l]["d"] == jsd_dicts[k]["d"]:
                    return -1.0
            if tx == tz1:
                if jsd_dicts[l]["d"] == jsd_dicts[k]["d1"]:
                    return -1.0

    if len(jsd_dicts[k].keys()) == 3 and len(jsd_dicts[l].keys()) == 3:
        s = jsd_dicts[k]["s"]
        if s == jsd_dicts[l]["s"]:
            j = jsd_dicts[k]["t"]
            j1 = jsd_dicts[l]["t"]
            sz = subsequentStation(S[j], s)
            if s in trains_routes["Ttrack"].keys():
                if occursAsPair(j, j1, trains_routes["Ttrack"][s]):
                    return 0.5
    return 0.0

# penalties and objective
def penalty(k, tsd_dicts, Problem):
    """
    Function to calculate penalty of the train
    """
    t = tsd_dicts[k]["t"]
    s = tsd_dicts[k]["s"]
    w = penaltyWeights(Problem.trains_timing, t, s) / Problem.d_max
    return tsd_dicts[k]["d"] * w

def getCoupling(k, l, tsd_dicts, Problem):
    """
    Function to return weighted hard constrains contributions to Qmat at k,l in the case where no auxiliary variables
    """
    p_sum = Problem.p_sum
    p_pair = Problem.p_pair
    trains_routes = Problem.trains_routes
    trains_timing = Problem.trains_timing
    # conditions
    T = p_sum * pSum(k, l, tsd_dicts)
    T += p_pair * pHeadway(k, l, tsd_dicts, trains_timing, trains_routes)
    T += p_pair * pMinimalStay(k, l, tsd_dicts, trains_timing, trains_routes)
    T += p_pair * pSingleTrack(k, l, tsd_dicts, trains_timing, trains_routes)
    T += p_pair * pSwitchOccupation(k, l, tsd_dicts, trains_timing, trains_routes)
    return T

def getZCoupling(k, l, tsd_dicts, Problem):
    """ 
    Function to return weighted hard constrains contributions to Qmat at k,l in the case where auxiliary variables are included
    """
    trains_timing = Problem.trains_timing
    trains_routes = Problem.trains_routes
    T = Problem.p_pair * pTrackOccupationConditionQuadraticPart(k, l, tsd_dicts, trains_timing, trains_routes)
    T += Problem.p_qubic * pRosenbergDecomposition(k, l, tsd_dicts, trains_routes)
    return T

def makeQubo(Problem):
    """
    Function to encode problem to QUBO matrix
    """
    inds, q_bits = indexingForQubo(Problem.trains_routes, Problem.trains_timing, Problem.d_max) 
    inds_z, q_bits_z = zIndices(Problem.trains_routes, Problem.d_max)
    inds1 = np.concatenate([inds, inds_z])
    Q = [[0.0 for _ in range(q_bits + q_bits_z)] for _ in range(q_bits + q_bits_z)]

    #add objective
    for k in range(q_bits):
        Q[k][k] += penalty(k, inds, Problem)
    #quadratic headway, minimal stay, single_line, circulation, switch conditions
    for k in range(q_bits):
        for l in range(q_bits):
            Q[k][l] += getCoupling(k, l, inds, Problem)
    #qubic track occupancy condition
    for k in range(q_bits + q_bits_z):
        for l in range(q_bits + q_bits_z):
            Q[k][l] += getZCoupling(k, l, inds1, Problem)
    return Q