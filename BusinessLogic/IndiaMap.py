from flask import Markup

class IndiaMapModel:

    def __init__(self , title , subtitle , html):
        self.Title = title
        self.Subtitle = subtitle
        self.Html = Markup(html._repr_html_())