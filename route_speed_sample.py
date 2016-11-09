"""Generate statistics on measurement error.

Error for Poisson process sampling over GRT routes at constant speed.
"""
import math
import os
import pyproj
from shapely.geometry import LineString


def read_csv(fp):
    results = []
    headline = fp.readline()
    headings = headline.strip().split(',')
    for line in fp:
        tokens = line.strip().split(',')
        results.append({k: v for k, v in zip(headings, tokens)})
    return results

speed = 50.0 / 3.6  # km/h to m/s
cache_rate = 30
sample_rate = - math.log(0.205) / 30.0
last_sampled_pos = 0
next_sample_interval = 0
errors_x = []
errors_y = []
proj = pyproj.Proj(proj='utm', zone=17, ellps='WGS84')

grt_folder = 'data/gtfs'
with open(os.path(grt_folder, 'shapes.txt')) as fp:
    shape_lines = read_csv(fp)
shape_data = {}
for line in shape_lines:
    shape_id = line['shape_id']
    if shape_id not in shape_data:
        shape_data[shape_id] = []
    shape_data[shape_id].append(line)
shapes = {}
for shape_id in shape_data:
    shape_data[shape_id].sort(lambda b: b['shape_pt_sequence'])
    points = []
    for line in shape_data[shape_id]:
        pt = proj(line['shape_pt_lon'], line['shape_pt_lat'])
        points.append(list(pt))
    shapes[shape_id] = LineString(points)

with open(os.path(grt_folder, 'trips.txt')) as fp:
    trip_lines = read_csv(fp)
shapes_sequence = [trip['shape_id'] for trip in trip_lines]
