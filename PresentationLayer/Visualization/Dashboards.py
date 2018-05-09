from flask import Blueprint,render_template , Markup
from jinja2 import TemplateNotFound

from BusinessLogic.Mapping import *
from BusinessLogic.FileOps import *

import os
from config import files

Dashboards = Blueprint('Dashboards', __name__)


@Dashboards.route('/')
def importantDashboards():
    try:
        
        dashboards= [ "/plot/scatter/TourismIndiaOverYears/1/4/0?returnPartial=True" ]

        return render_template('Dashboards/Base.html' ,dashboard_links = dashboards)

    except TemplateNotFound:
        abort(404)


@Dashboards.route('/mutualFunds')
def mutualFunds():
    try:
        
        dashboards= ['/plot/scatter/MutualFundPerformance/{}/{}/0?returnPartial=True'.format(i,i+1) for i in range(3,10)]

        return render_template('Dashboards/Base.html' ,dashboard_links = dashboards)

    except TemplateNotFound:
        abort(404)
