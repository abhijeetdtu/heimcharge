import os

workers = int(os.environ.get('GUNICORN_PROCESSES', '3'))
threads = int(os.environ.get('GUNICORN_THREADS', '1'))

forwarded_allow_ips = '*'
secure_scheme_headers = { 'X-Forwarded-Proto': 'https' }


plotting = { "India" : { "Center" : { "Lat" :  20.5937, "Long" : 78.9629 } } , "DefaultZoom": 4}