#!/usr/bin/env python

import tarfile
import pymongo
import pyproj
from glob import glob
from google.transit import gtfs_realtime_pb2
from contextlib import closing
from datetime import datetime

proj = pyproj.Proj(proj='utm', zone=17, ellps='WGS84')

client = pymongo.MongoClient()
db = client.transitdb
collection = db.rt_samples
collection.create_index([("loc", pymongo.GEOSPHERE)])
collection.create_index([
    ("startdate", pymongo.ASCENDING),
    ("trip", pymongo.ASCENDING),
    ("timestamp", pymongo.ASCENDING)
], unique=True)

processed_times = []
feed = gtfs_realtime_pb2.FeedMessage()

for filename in glob('/Users/mboos/grt/exploration/data/vehicle-positions-*.tar.gz'):
    print filename
    last_samples = {}
    with tarfile.open(filename) as tf:
        for member in tf.getmembers():
            records = []
            try:
                with closing(tf.extractfile(member)) as fp:
                    feed.ParseFromString(fp.read())
            except:
                continue
            if feed.header.timestamp in processed_times or not feed.header.timestamp:
                continue
            processed_times.append(feed.header.timestamp)
            timestamp = datetime.fromtimestamp(feed.header.timestamp)
            print timestamp
            for entity in feed.entity:
                vehicle = entity.vehicle
                route = vehicle.trip.route_id
                trip = vehicle.trip.trip_id
                startdate = vehicle.trip.start_date
                starttime = vehicle.trip.start_time
                lat = vehicle.position.latitude
                lon = vehicle.position.longitude
                next_or_current_stop = vehicle.current_stop_sequence
                status = vehicle.current_status
                vid = entity.id
                bad = False
                x, y = proj(lon, lat)
                run = (startdate, trip)

                if lat == 0 or lon == 0:
                    bad = True
                elif run in last_samples:
                    last = last_samples[run]
                    if lat == last['lat'] and lon == last['lon']:
                        bad = True
                last_samples[run] = {
                    'lat': lat,
                    'lon': lon
                }
                records.append(pymongo.UpdateOne({
                    'startdate': startdate,
                    'trip': trip,
                    'timestamp': timestamp
                }, {"$set": {
                    'loc': {
                        'type': 'Point',
                        'coordinates': [lon, lat]
                    },
                    'route': route,
                    'starttime': starttime,
                    'next_or_current_stop': next_or_current_stop,
                    'status': status,
                    'vehicle': vid,
                    'xy': [x, y],
                    'bad': bad
                }}, upsert=True))
            if records:
                collection.bulk_write(records)
