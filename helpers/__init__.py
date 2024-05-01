""" 
Initialise import functions from other libraries
"""
from encoders.QUBO_encoder import penaltyWeights, subsequentStation, occursAsPair, earliestDepartureTime, tau, departureStationForSwitches, indexingForQubo, getCoupling, zIndices, getZCoupling, penalty, pTrackOccupationConditionQuadraticPart, pRosenbergDecomposition, pSwitchOccupation, pHeadway, pMinimalStay, pSingleTrack, makeQubo
from .helpers_functions_QUBO import energy, previousStation
