import os

class DBConfig:
    root_dir = os.path.dirname(__file__)
    path_to_db = os.path.abspath(os.path.join(root_dir , "heimdb"))
    path_to_init_sql = os.path.abspath(os.path.join(root_dir , "InitSQL"))
