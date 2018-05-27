import geopy
import json

from geopy.geocoders import Nominatim
from config import locationCacheFile

geolocator = Nominatim()
locationCache = json.load(open(locationCacheFile))

def GetLocationLatLong(strAddress):
    if strAddress in locationCache:
        return locationCache[strAddress]

    try:
        location = geolocator.geocode(strAddress)
        if(type(location) == list):
            print(location)
            location = location[0]

        if(location == None):
            location = [0,0]
        else:
            location =  [location.latitude , location.longitude]

    except:
        location = [0,0]

    locationCache[strAddress] = location
    
    json.dump(locationCache , open(locationCacheFile , "w"))
    return location


def AddLatLongColumnsToDataframe(df , locationCol):
    for index,row in df.iterrows():
        lat,long = GetLocationLatLong(row[locationCol])
        df.loc[index]['Lat'] = lat
        df.loc[index]['Long'] = long

    return df