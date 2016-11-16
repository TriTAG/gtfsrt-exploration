# gtfsrt-exploration

## Set up

-	Install MongoDB, Python 2 with pip
-	sudo pip2 install pymongo numpy pyproj protobuf gtfs-realtime-bindings matplotlib emcee shapely

Data folder:

-	Create a directory called `data` in the root of the repo
-	Create a directory (or symlink) at `data/gtfs` containing the GTFS data
	files (e.g. run `ln -s $HOME/grt-gtfs data/gtfs`).
-	Create a directory (or symlink) at `data/gtfs-rt` containing the
	de-duplicated GTFS-RT archive files ([download for GRT from
	here](https://www.timmclean.net/tritag/)).
