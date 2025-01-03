''' Generate isochrones for the libraries in the basic dataset for libraries 2023. '''

import csv
import json
import time
import os.path

import requests

DATA_SOURCE = './data/basic-dataset-for-libraries-2023-enhanced.csv'
OUTPUT_DIR = './data/isochrones/basic-dataset-for-libraries-2023'
ORS_API_KEY = ''

MODE = 'foot-walking'


def make_slug(text):
    ''' Create a slug from a text '''
    return text.lower().replace(' ', '-')


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

    location_types = ['start', 'destination']

    locations = []  # Array to store the locations for which isochrones will be generated
    for library in libraries:
        for location_type in location_types:

            # Example: https://api.openrouteservice.org/v2/isochrones/driving-car
            file_dir = OUTPUT_DIR + '/' + library['service'] + '/'
            base_file_name = make_slug(library['name']) + '_' + \
                library['longitude'] + '_' + \
                library['latitude'] + '_' + MODE + '_' + location_type

            file_path = file_dir + base_file_name + '.geojson'

            if not os.path.exists(file_path):
                locations.append({
                    'service': library['service'],
                    'name': library['name'],
                    'longitude': library['longitude'],
                    'latitude': library['latitude'],
                    'location_type': location_type,
                    'file_path': file_path
                })

    for location_type in location_types:

        # The call to the API can be done in batches of 5 locations at once
        batch_size = 5

        locations = [
            location for location in locations if location['location_type'] == location_type]

        location_batches = [locations[i:i + batch_size]
                            for i in range(0, len(locations), batch_size)]

        for batch in location_batches:

            attributes = ['total_pop']
            intervals = [300, 600, 900, 1200, 1500, 1800]

            # Locations is an array of lng/lat coordinates
            locations = []

            for location in batch:
                locations.append(
                    [float(location['longitude']), float(location['latitude'])])

            body = {
                'locations': locations,
                'range': intervals,
                'attributes': attributes
            }

            headers = {
                'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
                'Authorization': ORS_API_KEY}

            base_url = 'https://api.openrouteservice.org/v2/isochrones/'

            url = base_url + MODE

            response = requests.post(
                url, json=body, headers=headers, timeout=600)

            if response.status_code == 200:
                data = response.json()

                # Read the response and write each isochrone to a separate file
                # Isochrones are embedded in a geojson feature collection with group_index property
                # Create a feature collection for each group_index

                # For each location in the locations array create a new feature collection
                for (idx, location) in enumerate(batch):

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
                        location['file_path']), exist_ok=True)

                    # Write out the feature collection to a file
                    with open(location['file_path'], 'w', encoding='utf-8') as location_file:
                        json.dump(feature_collection, location_file)

                time.sleep(5)

            else:
                print('Error: ', response.status_code)


run()
