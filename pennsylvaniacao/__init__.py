import ogr
#from IPython import embed
import sys
import pkg_resources
import json
import os
import yaml
import csv
from geopy.geocoders import GoogleV3

from cgi import parse_qs, escape

config_file = "/etc/pennsylvaniacao.yml"
config = dict()
if os.path.isfile(config_file):
    with open(config_file, 'rU') as stream:
        config = yaml.load(stream)
google_client_id = config.get('google client id', None)
google_secret = config.get('google secret', None)
if google_client_id is not None and google_secret is not None:
    my_geocoder = GoogleV3(client_id=google_client_id, secret_key=google_secret)
else:
    my_geocoder = GoogleV3()

info = dict()
infofile = pkg_resources.resource_filename(pkg_resources.Requirement.parse('pennsylvaniacao'), 'pennsylvaniacao/data/info.csv')
with open(infofile) as infile:
    for line in csv.reader(infile):
        info[line[0]] = dict(address=line[1], fulladdress=line[2], contact=line[3], latitude=line[4], longitude=line[5])

shapefile = pkg_resources.resource_filename(pkg_resources.Requirement.parse('pennsylvaniacao'), 'pennsylvaniacao/data/cao_2016.shp')
drv = ogr.GetDriverByName('ESRI Shapefile')
#sys.stderr.write("Shapefile is " + str(shapefile) + "\n")
ds_in = drv.Open(shapefile)
if ds_in is not None:
    lyr_in = ds_in.GetLayer(0)
    idx_reg = lyr_in.GetLayerDefn().GetFieldIndex("nam_dist")
    geo_ref = lyr_in.GetSpatialRef()
    point_ref = ogr.osr.SpatialReference()
    point_ref.ImportFromEPSG(4326)
    ctran = ogr.osr.CoordinateTransformation(point_ref,geo_ref)

def application(environ, start_response):
    parameters = parse_qs(environ.get('QUERY_STRING', ''))
    if 'lat' in parameters and 'lon' in parameters:
        district = cao_district(float(parameters['lon'][0]), float(parameters['lat'][0]))
    elif 'address' in parameters:
        geocode_results = my_geocoder.geocode(parameters['address'][0])
        if geocode_results:
            district = cao_district(float(geocode_results.longitude), float(geocode_results.latitude))
        else:
            district = None
    elif 'street' in parameters:
        if 'state' in parameters:
            state = unicode(parameters['state'][0])
        else:
            state = u'PA'
        if 'city' in parameters:
            city = unicode(parameters['city'][0])
        else:
            city = u'Philadelphia'
        address = unicode(parameters['street'][0]) + u', ' + city + u', ' + state
        geocode_results = my_geocoder.geocode(address)
        if geocode_results:
            district = cao_district(float(geocode_results.longitude), float(geocode_results.latitude))
        else:
            district = None
    else:
        district = None
    result = dict()
    if district is None:
        result['success'] = 0
    else:
        result['success'] = 1
        result['district'] = district
        if district in info:
            result['latitude'] = info[district]['latitude']
            result['longitude'] = info[district]['longitude']
            result['contact'] = info[district]['contact']
            result['fulladdress'] = info[district]['fulladdress']
    start_response('200 OK', [('Content-Type', 'application/json')])
    return [json.dumps(result)]

def search(**kwargs):
    result = kwargs.get('result', dict())
    if 'lat' in kwargs and 'lon' in kwargs:
        district = cao_district(float(kwargs['lon']), float(kwargs['lat']))
    elif 'address' in kwargs:
        geocode_results = my_geocoder.geocode(kwargs['address'])
        if geocode_results:
            district = cao_district(float(geocode_results.longitude), float(geocode_results.latitude))
        else:
            district = None
    elif 'street' in kwargs:
        if 'state' in kwargs:
            state = unicode(kwargs['state'])
        else:
            state = u'PA'
        if 'city' in kwargs:
            city = unicode(kwargs['city'])
        else:
            city = u'Philadelphia'
        address = unicode(kwargs['street']) + u', ' + city + u', ' + state
        geocode_results = my_geocoder.geocode(address)
        if geocode_results:
            district = cao_district(float(geocode_results.longitude), float(geocode_results.latitude))
        else:
            district = None
    else:
        district = None
    result = dict()
    if district is None:
        result['success'] = 0
    else:
        result['success'] = 1
        result['district'] = district
        if district in info:
            result['latitude'] = info[district]['latitude']
            result['longitude'] = info[district]['longitude']
            result['contact'] = info[district]['contact']
            result['fulladdress'] = info[district]['fulladdress']
            result['address'] = info[district]['address']
    return result

def cao_district(lon, lat):
    [lon,lat,z] = ctran.TransformPoint(lon,lat)

    pt = ogr.Geometry(ogr.wkbPoint)
    pt.SetPoint_2D(0, lon, lat)

    lyr_in.SetSpatialFilter(pt)

    for feat_in in lyr_in:
        return(feat_in.GetFieldAsString(idx_reg))
    return(None)
