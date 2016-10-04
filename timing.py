from google.transit import gtfs_realtime_pb2
from glob import glob

feed = gtfs_realtime_pb2.FeedMessage()

lastTime = 0
cnt = 0
offCnt = 0
for filename in glob('/Users/mboos/grt/vehicle-positions-archive-20160727-010341-323824221/*'):
    with open(filename) as fp:
        feed.ParseFromString(fp.read())
    #for entity in feed.entity:
    #    print entity
    ts = feed.header.timestamp
    if ts == lastTime:
        continue
    elif lastTime != 0:
        cnt += 1
        if ts - lastTime != 30:
            print ts - lastTime,  int(cnt/120+1), (cnt % 120)/2
            offCnt += 1
    lastTime = ts

print float(offCnt)/cnt*100.0
