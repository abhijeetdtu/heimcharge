from flask import Blueprint,render_template  , url_for , request ,abort, Response,render_template_string , redirect
from flask import jsonify

import json
from uuid import uuid4
import os

from BusinessLogic.FileOps import GetJSONFromFileOrObj
from Database.Blogs import Blog , BlogModel

Blogs = Blueprint('Blogs', __name__)

def GetPathFromId(id):
    return os.path.abspath(os.path.join("." , "BlogData", id))

def GetBlogModel(request):
    js = request.get_json()
    id = js["id"]
    path = GetPathFromId(id)
    return BlogModel(id,path ,js)

@Blogs.route("/")
def Index():
    return render_template("Blog/Landing.html" , blogs = Blog().GetAll())

@Blogs.route("/get/<string:uid>")
def Get(uid):
    path = GetPathFromId(uid)
    return jsonify(json.load(open(path)))

@Blogs.route("/new")
def New():
    return redirect(url_for(".Create" , uid= uuid4()))

@Blogs.route("/create/<string:uid>")
def Create(uid):
    return render_template("Blog/Editor.html" , id=uid)

@Blogs.route("/save" , methods=["POST"])
def Save():
    model = GetBlogModel(request)
    Blog().Save(model)
    return jsonify({"saved":True , "id":model.id})
