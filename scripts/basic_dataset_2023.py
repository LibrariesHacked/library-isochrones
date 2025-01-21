''' Generate isochrones for the libraries in the basic dataset for libraries 2023. '''

import csv
import json
import time
import os.path

import requests

DATA_SOURCE = './../data/basic-dataset-for-libraries-2023-enhanced.csv'
OUTPUT_DIR = './../data/isochrones/basic-dataset-2023'
OUTPUT_CSV = OUTPUT_DIR + '/basic-dataset-2023-analysis.csv'
SINGLE_GEOJSON = OUTPUT_DIR + '/basic-dataset-2023.geojson'

ORS_URL = 'https://api.openrouteservice.org/v2/isochrones/'
ORS_API_KEY = ''

MODE = 'foot-walking'
LOCATION_TYPES = ['destination']
ATTRIBUTES = ['area', 'total_pop', 'reachfactor']
INTERVALS = [5, 10, 15, 20, 25, 30]


def make_slug(text):
    ''' Create a slug from a text '''
    return text.lower().replace(' ', '-').replace('/', '-')


def add_isochrones_to_array(location_data, location_obj, array):
    ''' Add isochrones to the array '''
    features = location_data['features']
    for feature in features:
        feature['properties']['service'] = location_obj['service']
        feature['properties']['name'] = location_obj['name']
        feature['properties']['longitude'] = location_obj['longitude']
        feature['properties']['latitude'] = location_obj['latitude']
        array.append(feature)


def add_isochrone_props(location_data, obj):
    ''' Add isochrone properties to the object '''
    features = location_data['features']
    # 15 min isochrone has a property value of seconds = 900.0
    # 30 min isochrone has a property value of seconds = 1800.0
    # Find each isochrone and get the area, total_pop and reachfactor
    for feature in features:
        minutes = round(feature['properties']['value'] / 60)

        for interval in INTERVALS:
            if minutes == interval:
                for attribute in ATTRIBUTES:
                    obj[str(interval) + 'm_' +
                        attribute] = feature['properties'][attribute]


def run():
    ''' Generate isochrones '''
    libraries = []
    with open(DATA_SOURCE, 'r', encoding='utf-8') as library_file:
        library_reader = csv.reader(library_file, delimiter=',', quotechar='"')
        next(library_reader, None)  # skip the header

        for row in library_reader:

            entry_type = row[3]
            statutory = row[19]

            if entry_type == 'Static Library' and statutory == 'Yes':
                library = {'service': row[0], 'name': row[2],
                           'longitude': row[11], 'latitude': row[12]}
                libraries.append(library)

    all_isochrone_features = []
    locations = []  # Array to store the locations for which isochrones will be generated
    for library in libraries:
        for location_type in LOCATION_TYPES:
            file_dir = OUTPUT_DIR + '/' + library['service'] + '/'
            base_file_name = make_slug(library['name']) + '_' + \
                library['longitude'] + '_' + \
                library['latitude'] + '_' + MODE + '_' + location_type

            file_path = file_dir + base_file_name + '.geojson'

            location_obj = {
                'service': library['service'],
                'name': library['name'],
                'longitude': library['longitude'],
                'latitude': library['latitude'],
                'location_type': location_type,
                'file_path': file_path
            }
            if not os.path.exists(file_path):
                location_obj['complete'] = False
            else:
               # Get the data from the file
                with open(file_path, 'r', encoding='utf-8') as location_file:
                    location_data = json.load(location_file)
                    add_isochrone_props(location_data, location_obj)
                    location_obj['complete'] = True

                    add_isochrones_to_array(
                        location_data, location_obj, all_isochrone_features)
            locations.append(location_obj)

    for location_type in LOCATION_TYPES:

        # The call to the API can be done in batches of 5 locations at once
        batch_size = 5

        type_locations = [
            location for location in locations if location['location_type'] == location_type and not location['complete']]

        location_batches = [type_locations[i:i + batch_size]
                            for i in range(0, len(type_locations), batch_size)]

        for batch in location_batches:

            latlngs = []

            for batch_item in batch:
                latlngs.append(
                    [float(batch_item['longitude']), float(batch_item['latitude'])])

            # Create a new array of seconds from the intervals
            interval_seconds = [interval * 60 for interval in INTERVALS]
            body = {
                'locations': latlngs,
                'range': interval_seconds,
                'attributes': ATTRIBUTES
            }

            headers = {
                'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8', 'Authorization': ORS_API_KEY}

            url = ORS_URL + MODE

            response = requests.post(
                url, json=body, headers=headers, timeout=600)

            if response.status_code == 200:
                data = response.json()

                # Read the response and write each isochrone to a separate file
                # Isochrones are embedded in a geojson feature collection with group_index property
                # Create a feature collection for each group_index

                # For each item in the batch array create a new feature collection
                for (idx, batch_item) in enumerate(batch):

                    feature_collection = {
                        'type': 'FeatureCollection',
                        'features': []
                    }
                    for feature in data['features']:
                        group_index = feature['properties']['group_index']
                        if group_index == idx:
                            feature_collection['features'].append(
                                feature)

                    # Create the directory if it does not exist
                    os.makedirs(os.path.dirname(
                        batch_item['file_path']), exist_ok=True)

                    # Write out the feature collection to a file
                    with open(batch_item['file_path'], 'w', encoding='utf-8') as location_file:
                        json.dump(feature_collection, location_file)

                    # Get the original location object and add the isochrone properties
                    for loc in locations:
                        if loc['file_path'] == batch_item['file_path']:
                            add_isochrone_props(feature_collection, loc)
                            loc['complete'] = True
                            add_isochrones_to_array(
                                feature_collection, loc, all_isochrone_features)

                time.sleep(5)

            else:
                print(body)

    # Now write out a CSV for all the locations array
    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as locations_file:
        location_writer = csv.writer(locations_file, delimiter=',',
                                     quotechar='"', quoting=csv.QUOTE_MINIMAL)
        headers = ['service', 'name', 'longitude', 'latitude', 'location_type']
        for interval in INTERVALS:
            for attribute in ATTRIBUTES:
                headers.append(str(interval) + 'm_' + attribute)

        location_writer.writerow(headers)
        row = []
        for location in locations:
            row = [location['service'], location['name'], location['longitude'],
                   location['latitude'], location['location_type']]
            for interval in INTERVALS:
                for attribute in ATTRIBUTES:
                    if location['complete']:
                        row.append(location[str(interval) + 'm_' + attribute])

            location_writer.writerow(row)

    # Write out a single geojson file with all the isochrones
    with open(SINGLE_GEOJSON, 'w', encoding='utf-8') as single_file:
        single_file.write('{"type":"FeatureCollection","features":[')
        for (idx, feature) in enumerate(all_isochrone_features):
            if idx > 0:
                single_file.write(',')
            single_file.write(json.dumps(feature))
        single_file.write(']}')


run()
