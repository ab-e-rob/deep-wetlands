import time

import geojson
import geopandas
import requests
from matplotlib import pyplot as plt


def download_country_boundaries(iso, adm, file_name):
    # ISO = 'SWE'  # "DEU" is the ISO code for Germany
    # ADM = 'ADM2'  # Equivalent to administrative districts

    # Query geoBoundaries
    r = requests.get("https://www.geoboundaries.org/gbRequest.html?ISO={}&ADM={}".format(iso, adm))
    dl_path = r.json()[0]['gjDownloadURL']

    # Save the result as a GeoJSON
    # filename = 'geoboundary.geojson'
    geoboundary = requests.get(dl_path).json()
    with open(file_name, 'w') as file:
        geojson.dump(geoboundary, file)


def get_region_boundaries(shape_name, file_name):

    # Read data using GeoPandas
    geoboundary = geopandas.read_file(file_name)
    print("Data dimensions: {}".format(geoboundary.shape))

    return geoboundary


def show_region_boundaries(geoboundary, shape_name):
    geoboundary.sample(3)
    # shape_name = 'Sala kommun'
    fig, ax = plt.subplots(1, figsize=(10, 10))
    geoboundary[geoboundary.shapeName == shape_name].plot('shapeName', legend=True, ax=ax)
    plt.show()


def main():

    file_name = '/tmp/sweden.geojson'
    download_country_boundaries('SWE', 'ADM2', file_name)
    get_region_boundaries('Sala kommun', file_name)


# start = time.time()
# main()
# end = time.time()
# total_time = end - start
# print("%s: Total time = %f seconds" % (time.strftime("%Y/%m/%d-%H:%M:%S"), total_time))