import os

workers = int(os.environ.get('GUNICORN_PROCESSES', '3'))
threads = int(os.environ.get('GUNICORN_THREADS', '1'))

forwarded_allow_ips = '*'
secure_scheme_headers = { 'X-Forwarded-Proto': 'https' }

files = {
    "StateWisePop" : os.path.abspath(os.path.join("Data" , "stateWisePopulation.json")),
    "StateWisePop" : os.path.abspath(os.path.join("Data" , "stateWisePopulation.json")),
    "LanguageWiseMovies" : os.path.abspath(os.path.join("Data" , "LanguageWiseMovies.json"))
    }
plotting = { "India" : { "Center" : { "Lat" :  20.5937, "Long" : 78.9629 } }
, "DefaultZoom": 4
, "SelectedScheme" : "Blackish"
, "ColorSchemes" : {
     "Blueiss":["#6c567b","#c06c84","#f67280","#f8b195"]
    ,"Blackish":["#0A0D0D","#2D3536","#627676","#BFCCCC"]
    ,"Pie":["#0A0D0D","#2D3536","#627676","#BFCCCC","#6c567b","#c06c84","#f67280","#f8b195"]
    }
, "Pie":{
        "label_max_length":40
  }
}

locationCacheFile = "locationCache.json"
