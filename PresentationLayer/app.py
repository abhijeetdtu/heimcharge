from flask import Flask , Markup
from plotly.offline import plot
from plotly.graph_objs import Scatter

application = Flask(__name__)

@application.route("/")
def hello():
    my_plot_div = plot([Scatter(x=[1, 2, 3 , 5], y=[3, 1, 6 , 15])], output_type='div')
    return Markup(my_plot_div)
