# Driving distances using OpenStreetMaps

This project evaluates the driving distances of vehicles per day using the road network from OSM. The distances are stored in a DB and served by a REST service using Docker.

## TLDR

```bash
git clone git@github.com:diegopso/driving-distances.git
cd driving-distances/
make build
make test
make run-job
make run-service
make call-service
```

## Compatibility

This repository was tested on Ubuntu 18 and on Windows 10 using WSL2 with Ubuntu 20.

## Dependencies

In order to use this project it is needed to install [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/). There are many recipes to make easier to use this repo made with [Makefile](https://www.gnu.org/software/make/manual/make.html). Also, the target `call-service` in the `Makefile` uses [curl](https://curl.se/).

## Configuration

To install the solution, just clone this repository and run the `build` target in the `Makefile`. After that the solution is ready to run tests, the main job, and the webservice. The indicated order to execute this targets can be seen in the TLDR section.

## Makefile Recipes

Many recipes to make easier to use this repo are available in the `Makefile`, among them:
- `build` builds the job and web service
- `test` runs the tests
- `run-job` launches the job locally
- `run-service` launches the service locally
- `call-service` calls the service with an example request

## REST End-point

An end-point is available on the host machine after runing the target `run-service` to consume the data generated in the job. This end-point is a `GET` method available by default at `http://localhost:8000/api/driven-distance`. The following query params can be used:

- `vehicle_id`: to be used when filtering data for a speciffic vehicle.
- `start_date`: to be used when filtering data after a certain date.
- `end_date`: to be used when filtering data before a certain date.

The end-point returns `JSON` and all these request parameters can be used combined.

## Solution Structure

The solution implemented in this repository consist of a pipeline using Python and hosted in a container named `job`, and a web service that provides a REST end-point to consumed the proccessed data. The complete structure of the solution can be seen in the figure below.

![challenge-architecture](https://user-images.githubusercontent.com/1905937/228333595-09ff5547-da9b-4402-b4b4-527b8849e6de.png)

The pipeline has the following steps:

1. Extract CSV: where the [pandas](https://pandas.pydata.org/) library is used to read the CSV file and perform preliminary formating, such as, changing the timezone of the dates.
2. Extract OSM data - once with the CSV data it is possible to identify the bounding box of the trips. This bounding box is used to export data from [OpenStreetMaps](https://wiki.openstreetmap.org/wiki/API) using their API through the library [OSMnx](https://osmnx.readthedocs.io/en/stable/). OSMnx is a library to download and work with data from OpenStreetMaps developed on top of [NetworX](https://networkx.org/), a well-known python library to work with graphs.
3. Coordinates to nodes: in the CSV file, the positions of the vehicles are stored as latitude and longitudes. These coordinates must be tranformed to graph nodes in the OSM graph using again OSMnx.
4. Identify trip segments: since each observation is a point of presence of the vehicle, it is possible to combine sequential observation to identify trip segments of the vehicles using pandas.
5. Estimate distances: The trip segments are used to evaluate driving distances using the OSM data. In some ocasions, the distance traversed between two sequential observations is small, resulting in a trip segment that starts and finishes in the same graph node. For these cases, a fallback is used to evaluate the straight-line distance between the origin and destination coordintates of the trip segment.
6. Group and save: Finally, the trip segments are grouped according to the day they took place and saved to the DB that is used to provide the REST end-point.

A [MySQL](https://www.mysql.com/) database is used to store the processed data. This database is consumed by a container where the REST end-point is implemented using [Python](https://www.python.org/) and [Flask](https://flask.palletsprojects.com/en/2.2.x/). These technologies were used because they provide a simple and easy-to-use alternative to quickly implement a web service. The end-point is served using [Nginx](https://www.nginx.com/) a well-known and generally well-performant web server.

The pipeline, database, Python/Flask end-point, and web server are managed using Docker and Docker Compose to ease the deployment of the solution.

## Folder Structure

```
├── .docker         # stores Dockerfiles and other container-related configuration files for the containers.
├── input           # stores `csv` files to be extracted. Columns: "vehicle_id","location_raw_lat","location_raw_lon","created_timestamp".
├── job             # store the python files responsible for extracting the `csv` files and storing in the database.
|   ├── ddmc        # the job package.
|   └── tests       # the job tests using Pytest and TestContainers.
├── output          # used as working directory when extracting the data from the `csv` files. Also stores the DB files.
└── service         # stores the python files for the web service.
```
