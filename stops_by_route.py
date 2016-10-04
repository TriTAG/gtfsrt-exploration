#!/usr/bin/env python

import pymongo

client = pymongo.MongoClient()
db = client.transitdb
collection = db.rt_samples

print "Route\t% Time Stopped"

routes = collection.distinct('route')
routes.sort(key=lambda x: int(x))
for route in routes:
    stop_times = collection.count({'bad': False, 'route': route, 'status': 1})
    all_times = collection.count({'bad': False, 'route': route})

    print '{}\t{:.1f}%'.format(route, float(stop_times)/all_times*100.0)
