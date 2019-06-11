import sqlite3
import os

from Database.config import DBConfig

def connection():
    return sqlite3.connect(DBConfig.path_to_db)

class InitDB:

    def __init__(self):
        print(DBConfig.path_to_db)
        self.connection = sqlite3.connect(DBConfig.path_to_db)
        self.Init()

    def Init(self):
        for file in sorted(os.listdir(DBConfig.path_to_init_sql) , reverse=True):
            full_path = os.path.join(DBConfig.path_to_init_sql , file)
            if file.find(".sql") >= 0:
                self.connection.execute(open(full_path , "r").read())


if __name__ =="__main__":
    InitDB()
