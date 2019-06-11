import json
from Database.BaseClass import DatabaseBase

class BlogModel:

    def __init__(self,id,path,content):
        self.id = id
        self.path = path
        self.js = content

class Blog(DatabaseBase):

    def __init__(self):
        super(Blog,self).__init__("Blog")

    def Save(self , blogModel):
        sql = """
        INSERT INTO Blog values('{}' , '{}')
        """.format(blogModel.id , blogModel.path)
        json.dump(blogModel.js , open(blogModel.path, "w"))
        self.Exec(sql)
