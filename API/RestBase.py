import json
import requests
import os
class Rest:

    #API_KEY = "54f6530135d98e6597e84b5f4009de12"
    API_KEY = "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"
    RESOURCE_KEY_FILE = os.path.abspath(os.path.join("." ,"API", "resource_keys.json"))
    BASE_URL = "https://api.data.gov.in/resource/{0}?api-key={1}&format={2}&limit={3}&offset={4}"

    ResourceKeys = json.load(open(RESOURCE_KEY_FILE , "r"))

    @staticmethod
    def FilterDictToQueryParam(filters):
        params = ""
        if filters != None:
            for key,val in filters.items():
                params += "&filters[{0}]={1}".format(key , val)

        return params

    @staticmethod
    def GetAllData(resourceId,type="json" ,limit=50 ,filters=None):
        records = []
        offset = 0
        prev=""
        if limit == -1:
            limit = 50

        while True:
            js = Rest.GetJsonFromId(resourceId , type=type,offset=offset , limit=10 ,filters = filters)
            if offset > limit or prev == json.dumps(js):
                break
            prev = json.dumps(js)
            records.extend(js["records"])
            offset += 10

        return records

    @staticmethod
    def GetJsonFromId(resourceId,type="json" , limit=-1 , offset=0 , filters=None):
        url = Rest.BASE_URL.format(resourceId , Rest.API_KEY , type , limit , offset)
        url += Rest.FilterDictToQueryParam(filters)


        print(url)
        return requests.get(url).json()

    @staticmethod
    def GetJsonFromName(resourceName ,limit=10, filters=None):
        return Rest.GetAllData(Rest.ResourceKeys[resourceName] , limit=limit,filters=filters)
