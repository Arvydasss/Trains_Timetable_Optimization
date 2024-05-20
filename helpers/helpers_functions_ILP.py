"""
Helpers for ILP solver
"""
import numpy as np
from helpers import previousStation, occursAsPair 

def updateDictOfDicts(d1, d2):
    """
    Function to updates the nested dictionary for linear annealing
    """
    assert np.size(d2.keys()) == 1

    for k in d2.keys():
        if k in d1.keys():
            updateDictOfDicts(d1[k], d2[k])
        else:
            d1.update(d2)
    return d1

def getM(LHS, RHS, d_max):
    """
    Function to compute minimal value of the large number M for the order variable
    y ∈ [0,1] conditional inequality such that:
    LHS + delay >= RHS + delay - M y
    """
    return np.max([RHS + d_max - LHS, 1.0])

def canMO(t, tp, s, train_sets):
    """
    Function to check if trains t1 and t2 can meet and overtake (MO) in the line between station and previous station
    """
    T1 = train_sets["T1"]
    S = train_sets["Routes"]
    sp = previousStation(S[t], s)
    spp = previousStation(S[tp], s)

    if T1 == {}:
        return False
    if sp is None or spp is None:
        return False
    if sp != spp:
        return True
    if occursAsPair(t, tp, T1[sp][s]):
        return False
    return True

def trainsEnteringViaSameSwitches(train_sets, s, t, tp):
    """ 
    Function to check if trains are entering station using common subset od switches
    """
    if s in train_sets["Tswitch"].keys():
        v = train_sets["Tswitch"][s]
        are_switches = np.array([t in e and tp in e for e in v])
        if True in are_switches:
            return ('in', 'in') in [(v[i][t], v[i][tp]) for i in np.where(are_switches)[0]]
        return False
    return False
