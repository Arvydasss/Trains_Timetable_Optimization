"""
Read files to problem - file, which helps to read the data from .xml and .csv files. Helps to calculate and assgin values to problem.
"""
import csv
import xml.etree.ElementTree as ET

def readLocationLinksCsv():
    csv_file = 'data/LocationLinksData.csv'
    data = {}
    with open(csv_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            location_from = row['Location from'][:-1]  
            location_to = row['Location to'][:-1] 
            data[(location_from, location_to)] = int(row['Distance']) / 1000
    return data

def timeToMinutes(time_str):
    hours = int(time_str[:2])
    minutes = int(time_str[2:4])
    seconds = int(time_str[4:])
    total_minutes = hours * 60 + minutes + seconds / 60
    return int(total_minutes)

def filterScheduleXml(input_xml_path, output_xml_path, stations = "", trains=""):
    tree = ET.parse(input_xml_path)
    root = tree.getroot()
    threads = root.findall('.//Thread')

    if (trains != ""):
        removeUnusedTrains(root, threads, trains)

    if (stations != ""):
        removeUnusedStations(threads, stations)

    removeEmptyTrain(root, threads, trains)
    editStationsTypes(threads)   

    tree.write(output_xml_path)

def removeUnusedTrains(root, threads, trains):
    for thread in threads:
        train_number = thread.attrib.get('train') 
        if (train_number not in trains):
            root.find('.//RegulatorySchedule').remove(thread)

def removeUnusedStations(threads, stations):
    for thread in threads:
        for event in thread.findall('Event'):
            esr_code = event.attrib.get('esr')
            if esr_code not in stations:
                thread.remove(event)

def removeEmptyTrain(root, threads, trains):
    for thread in threads:
        if len(thread) < 2:
            if (trains != ""):
                if (thread.attrib.get('train') in trains):
                    root.find('.//RegulatorySchedule').remove(thread)
            else:
                root.find('.//RegulatorySchedule').remove(thread)

def editStationsTypes(threads):
    for thread in threads:
        for index, event in enumerate(thread.findall('Event')):
            if (index == len(thread.findall('Event')) - 1):
                event.attrib['type'] = 'arrival'

def readScheduleXml(xml_file):
    locationLinks = readLocationLinksCsv()
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    trains = []
    t_pass = {}
    t_headway = {}
    t_stop = {}
    t_out = {}
    t_penalty = {}
    Routes = {}
    T = []
    T0 = {}
    T1 = {}
    Ttrack = {}
    Tswitch = {}

    readDataFromXml(root, trains)
    calculateOutPenaltyStopRoutesT(trains, t_out, t_penalty, t_stop, Routes, T)
    calculateHeadwayTrackT(Routes, t_headway, Ttrack, T1)
    calculateForSingleLine(Routes, T0, Tswitch)
    fixedRepeatedValues(Ttrack, T1, Tswitch)
    calculateStopAndPassingTime(trains, t_pass, t_stop, locationLinks)

    return assignValuesToProblem(t_pass, t_headway, t_stop, t_out, t_penalty, Routes, T, T1, T0, Ttrack, Tswitch)

def readDataFromXml(root, trains):
    for regulatory_schedule in root.findall('RegulatorySchedule'):
        for thread in regulatory_schedule.findall('Thread'):
            train_info = {
                'train': thread.attrib['train'],
                'events': []
            }
            for event in thread.findall('Event'):
                event_info = {
                    'esr': event.attrib['esr'],
                    'type': event.attrib['type'],
                    'time': timeToMinutes(event.attrib['time']),
                    'odd': event.attrib['odd'].lower() == 'true',
                    'stagename': event.attrib['stagename'].replace(' ', '_').replace('-', '_'),
                }
                if 'stage' in event.attrib:
                    event_info['stage'] = int(event.attrib['stage'])
                else:
                    event_info['stage'] = None
                train_info['events'].append(event_info)
            
            trains.append(train_info)

def calculateOutPenaltyStopRoutesT(trains, t_out, t_penalty, t_stop, Routes, T):
    for train_info in trains:
        train_id = train_info['train']
        route = []
        seen_stages = set()
        for i, event_info in enumerate(train_info['events']):
            stage_name = event_info['stagename']
            if stage_name not in seen_stages:
                route.append(stage_name)
                seen_stages.add(stage_name)

            if (i == 0):
                t_out[train_id + '_' + event_info['stagename']] = event_info['time']
                t_penalty[train_id + '_' + event_info['stagename']] = 0
            else:
                t_stop[train_id + '_' + event_info['stagename']] = 0
            
        Routes[train_id] = route
        T.append(train_id)

def calculateHeadwayTrackT(Routes, t_headway, Ttrack, T1):
    route_keys = list(Routes.keys())
    for i in range(len(route_keys) - 1):
        train_id_1 = route_keys[i]
        train_id_2 = route_keys[i+1]

        route_1 = Routes[train_id_1]
        route_2 = Routes[train_id_2]

        if (route_1 == route_2):
            for i in range(len(route_1) - 1):
                t_headway[train_id_1 + '_' + train_id_2 + '_' + route_1[i] + '_' + route_1[i+1]] = 2
                t_headway[train_id_2 + '_' + train_id_1 + '_' + route_1[i] + '_' + route_1[i+1]] = 2
            
            for j in range(len(route_1) - 1):
                station = route_1[j]
                next_station = route_1[j+1]
                
                if station not in Ttrack:
                    Ttrack[station]= [[train_id_1, train_id_2]]
                else:
                    Ttrack[station].append([train_id_1, train_id_2])
                
                if station not in T1:
                    T1[station] = {}
                if next_station not in T1[station]:
                    T1[station][next_station] = [[train_id_1, train_id_2]]
                else:
                    T1[station][next_station].append([train_id_1, train_id_2])
            
            last_station = route_1[-1]
            if last_station not in Ttrack:
                Ttrack[last_station] = [[train_id_1, train_id_2]]
            else:
                Ttrack[last_station].append([train_id_1, train_id_2])

def fixedRepeatedValues(Ttrack, T1, Tswitch):
    for key, value_list in Ttrack.items():
        Ttrack[key] = [uniqueValues(value_list)]

    for key, inner_dict in T1.items():
        for inner_key, value_list in inner_dict.items():
            inner_dict[inner_key] = [uniqueValues(value_list)]
    
    for key, value_list in Tswitch.items():
        Tswitch[key] = [mergeDictsInList(value_list)]

    for key, value in Tswitch.items():
        new_value = [{k: 'in' for k in value[0]}]
        Tswitch[key].extend(new_value)

def uniqueValues(lst):
    unique_vals = set()
    for sublist in lst:
        unique_vals.update(sublist)
    return list(unique_vals)

def mergeDictsInList(lst):
    merged_dict = {}
    for d in lst:
        if isinstance(d, dict):
            for key, value in d.items():
                if key not in merged_dict:
                    merged_dict[key] = 'in'
                if value == 'out':
                    merged_dict[key] = value
        elif isinstance(d, list):
            for sub_dict in d:
                for key, value in sub_dict.items():
                    if key not in merged_dict:
                        merged_dict[key] = 'in'
                    if value == 'out':
                        merged_dict[key] = value
    return merged_dict

def calculateStopAndPassingTime(trains, t_pass, t_stop, locationLinks):
    for train_info in trains:
            train_id = train_info['train']
            events = train_info['events']
            for i in range(len(events) - 1):
                event1 = events[i]
                event2 = events[i+1]
                key = f"{train_id}_{event1['stagename']}_{event2['stagename']}"
                distance = 5
                if (event1["esr"], event2["esr"]) in locationLinks:
                    distance = locationLinks[(event1["esr"], event2["esr"])]

                if (event2["esr"], event1["esr"]) in locationLinks:
                    distance = locationLinks[(event2["esr"], event1["esr"])]

                if (event1['stagename'] != event2['stagename']):
                    t_pass[key] = int(distance / 80 * 60)
                else:
                    t_stop[train_id + '_'+ event1['stagename']] = int(event2['time']) - int(event1['time'])

def calculateForSingleLine(Routes, T0, Tswitch):
    route_keys = list(Routes.keys())
    for i in range(len(route_keys) - 1):
        train_id_1 = route_keys[i]
        train_id_2 = route_keys[i+1]

        route_1 = Routes[train_id_1]
        route_2 = Routes[train_id_2]

        if (route_1 == route_2[::-1]):
            print(train_id_1)
            print(train_id_2)
            for j in range(len(route_1) - 1):
                station = route_1[j]
                next_station = route_1[j+1]
                conflict_key = (station, next_station)
                if conflict_key not in T0:
                    T0[conflict_key] = []

                if station not in Tswitch:
                    Tswitch[station] = [{train_id_1: "out", train_id_2: "out"}, {train_id_1: "in", train_id_2: "in"}]
                else:
                    Tswitch[station].append([{train_id_1: "out", train_id_2: "out"}, {train_id_1: "in", train_id_2: "in"}])

                if [train_id_1, train_id_2] not in T0[conflict_key]:
                    T0[conflict_key].append([train_id_1, train_id_2])

def assignValuesToProblem(t_pass, t_headway, t_stop, t_out, t_penalty, Routes, T, T1, T0, Ttrack, Tswitch):
    taus = {
        "t_pass": t_pass,
        "t_headway": t_headway,
        "t_stop": t_stop,
        "res": 1
    }

    trains_timing = {
        "tau" : taus,
        "t_out": t_out,
        "t_penalty": t_penalty
    }

    trains_routes = {
        "Routes": Routes,
        "T": T,
        "T0": T0,
        "T1": T1,
        "Ttrack": Ttrack,
        "Tswitch":Tswitch,
    }

    return taus, trains_timing, trains_routes