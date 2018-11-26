from flask import Blueprint,render_template , Markup
from flask import request,jsonify

from API.RestBase import *

import copy
import os

from config import files

AirQuality = Blueprint('AirQuality', __name__,template_folder='templates')


@AirQuality.route('/')
def show():
    filters = dict(city="Delhi" , pollutant_id="NO2")
    return jsonify(Rest.GetJsonFromName("AirQuality" ,limit=-1, filters=filters))
