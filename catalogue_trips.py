from google.transit import gtfs_realtime_pb2
from glob import glob
import pyproj
import math

import numpy as np
import matplotlib.pyplot as plt

feed = gtfs_realtime_pb2.FeedMessage()

routes = {}
samples = []
proj = pyproj.Proj(proj='utm', zone=17, ellps='WGS84')
num_samples = 0
good_samples = 0

for filename in glob('/Users/mboos/grt/vehicle-positions-archive-20160727-010341-323824221/*'):
    with open(filename) as fp:
        feed.ParseFromString(fp.read())
    if feed.header.timestamp in samples:
        continue
    samples.append(feed.header.timestamp)
    for entity in feed.entity:
        vehicle = entity.vehicle
        route = vehicle.trip.route_id
        trip = vehicle.trip.trip_id
        startdate = vehicle.trip.start_date
        lat = vehicle.position.latitude
        lon = vehicle.position.longitude
        next_or_current_stop = vehicle.current_stop_sequence
        status = vehicle.current_status
        vid = entity.id

        if route not in routes:
            routes[route] = {}
        if trip not in routes[route]:
            routes[route][trip] = {}
        if startdate not in routes[route][trip]:
            routes[route][trip][startdate] = {
                'vehicle': vid, 'points': []
            }
        points = routes[route][trip][startdate]['points']

        x, y = proj(lon, lat)
        points.append({
            'lat': lat, 'lng': lon, 'stop': next_or_current_stop,
            'status': status, 'x': x, 'y': y, 'time': feed.header.timestamp
        })

for route in routes:
    print route
    for trip in routes[route]:
        print '\t{0}'.format(trip)
        for startdate in routes[route][trip]:
            points = routes[route][trip][startdate]['points']
            speeds = []
            times = []
            dists = []
            for prv, nxt in zip(points[:-1], points[1:]):
                if prv['lat'] == 0 or nxt['lat'] == 0:
                    continue

                dist = math.sqrt((prv['x'] - nxt['x'])**2 +
                                 (prv['y'] - nxt['y'])**2)
                time = nxt['time'] - prv['time']
                speeds.append(dist/time)
                dists.append(dist)
                times.append(time)
            if trip == '136101401':
                x = np.asarray([step['time']-points[0]['time']
                                for step in points[1:]])
                y = np.asarray(speeds)
                x2 = np.asarray([step['time']-points[0]['time']
                                for step, speed in zip(points[1:], speeds)
                                if step['status'] == 1 and speed != 0])
                y2 = np.ones_like(x2)
                x3 = np.asarray([step['time']-points[0]['time']
                                for step, speed in zip(points[1:], speeds)
                                if speed == 0])
                y3 = np.ones_like(x3)
                print speeds
                line,  = plt.plot(x, y, '-', label='Sampled movement')
                stops, = plt.plot(x2, y2, 'r8', label='Sampled stops')
                dups, = plt.plot(x3, y3, 'kx', label='Duplicate samples')
                x4 = np.asarray([p['time']-points[0]['time'] for p in points[1:]])
                y4 = np.asarray([p2['stop']-p1['stop'] for p1, p2 in zip(points[:-1], points[1:])])
                st, = plt.plot(x4, y4, 'g', label='Next stop')
                plt.legend()
                plt.xlabel('Time (s)')
                plt.ylabel('Speed (m/s)')
                plt.show()
            num_samples += len(points) - 1
            good_samples += len([s for s in speeds if s == 0])
            if speeds:
                print '\t\t{0} {1} {2}% {3}'.format(startdate, len(points)/2,
                                                   float(len([s for s in speeds if s ==0]))/len(speeds)*100.0,
                                                   sum(dists)/sum(times))

print good_samples, num_samples
