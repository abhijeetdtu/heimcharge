import json
from uuid import uuid4

from flask import request
from flask_restful import Resource, Api

from PresentationLayer.app import application

BlogsAPI = Api(application , prefix="blogsapi")

class BlogResource(Resource):

    def get(self,user_id,blog_id):
        return json.load(open("/Blog/{}/{}".format(user_id , blog_id)))

    def put(self,user_id,blog_id):
        id = uuid4()
        js = request.get_json()
        json.dump(js , open("/Blog/{}/{}".format(user_id , id)))
        return js

BlogsAPI.add_resource(BlogResource, '/<string:user_id>/<string:blog_id>')
