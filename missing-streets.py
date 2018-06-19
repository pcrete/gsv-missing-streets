import os, math
import json
import overpass
import pandas as pd
import numpy as np
from tqdm import tqdm
from urllib.request import urlopen, HTTPError
from gsvloader import polygon_to_points, loader
from shapely.geometry import Polygon, Point, LineString, MultiLineString
from copy import deepcopy

def linestring_to_coords(roads):
    point_entry = {
        "type": "FeatureCollection",
        "features": []
    }
    for road in tqdm(roads['features'],'converting linestrings to coordinates'):
        if (road['geometry']['type'] != 'LineString'):
            continue
        
        line = deepcopy(road['geometry']['coordinates'])
        road['geometry']['coordinates'] = []
        
        for i in range(len(line)-1):
            x1,y1 = line[i]
            x2,y2 = line[i+1]
            x1 += 0.0000000001

            degree = math.degrees(math.atan(abs((y1-y2)/(x1-x2))))

            if(degree < 45): 
                if(x1 == min(x1,x2)): start_x,start_y, end_x,end_y = x1,y1, x2,y2 
                else: start_x,start_y, end_x,end_y = x2,y2, x1,y1

                m = (start_y-end_y)/(start_x-end_x)
                FROM, TO = start_x, end_x                      
                cur_x, cur_y = start_x, start_y
                while(FROM < TO):
                    new_x, new_y = linearEquation_x(start_x, start_y, m, FROM)
                    dist = math.hypot(new_x-cur_x, new_y-cur_y)
                    meters = 111111*dist
                    if(meters > 50):
                        cur_x, cur_y = new_x, new_y
                        road['geometry']['coordinates'].append([round(cur_x, 8), round(cur_y, 8)])  
                    FROM += 0.000000123
            else:
                if(y1 == min(y1,y2)): start_x,start_y, end_x,end_y = x1,y1, x2,y2 
                else: start_x,start_y, end_x,end_y = x2,y2, x1,y1

                m = (start_y-end_y)/(start_x-end_x)
                FROM, TO = start_y, end_y                      
                cur_x, cur_y = start_x, start_y
                while(FROM < TO):
                    new_x, new_y = linearEquation_y(start_x, start_y, m, FROM)
                    dist = math.hypot(new_x-cur_x, new_y-cur_y)
                    meters = 111111*dist
                    if(meters > 50):
                        cur_x, cur_y = new_x, new_y
                        road['geometry']['coordinates'].append([round(cur_x, 8), round(cur_y, 8)])  
                    FROM += 0.000000123
        point_entry['features'].append(road)
    return point_entry

def linearEquation_x(x1, y1, m, x):
    y = m*(x-x1)+y1
    return x,y

def linearEquation_y(x1, y1, m, y):
    x = (y - y1 + (m*x1)) / m
    return x,y


keys = pd.read_csv('api-keys.csv', header=None)

with open(os.path.join('data','shapefiles','นครศรีธรรมราช.geojson')) as f:
    data = json.load(f)
    
missing_all = {}
missing_all['features'] = []     

for feature in data['features']:
    prop = feature['properties']
    
    geojson_prop = {
        'PV_TN': prop['PV_TN'],
        'AP_TN': prop['AP_TN'],
        'TB_TN': prop['TB_TN']
    }
    
    entry = {
        'GEOJSON_PATH': os.path.join('data','shapefiles','นครศรีธรรมราช.geojson'),
        'keys': np.squeeze(keys.values)
    }
    
    polygon = polygon_to_points.get_polygon(entry, geojson_prop)
    
    roads = polygon_to_points.generate_overpass_script(polygon)
    
    point_geojson = linestring_to_coords(roads)
    
    no_missing = []
    missing_streets = deepcopy(point_geojson)
    for i, feature in enumerate(tqdm_notebook(point_geojson['features'], 'loading GSV')):

        has_missing = False
        missing_streets['features'][i]['geometry']['coordinates'] = []

        for lng, lat in feature['geometry']['coordinates']:
            requestMeta = urlopen(
                "https://maps.googleapis.com/maps/api/streetview/metadata?"+\
                "location="+str(lat)+','+str(lng)+"&key="+entry['keys'][0]
            )    
            metaJson = json.loads(requestMeta.read().decode('utf8'))
            if metaJson["status"] != 'OK':
                missing_streets['features'][i]['geometry']['coordinates'].append([lng, lat])
                has_missing = True

        if not has_missing: no_missing.append(i)
            
    for i in sorted(no_missing, reverse=True):
        del missing_streets['features'][i]
        
    missing_all.update(missing_streets)


missing_all.update({"type": "FeatureCollection"})

with open(os.path.join('data', 'v2', 'missing-all.geojson'), 'w') as FILE: 
    json.dump(missing_all, FILE, indent=4)