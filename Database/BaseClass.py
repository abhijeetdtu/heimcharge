from Database.Connection import connection

class DatabaseBase:

    def __init__(self,table , idCol):
        self.table = table
        self.idCol = idCol

    def GetAll(self):
        sql = """
        SELECT * FROM {}
        """.format(self.table)
        return self.Exec(sql)

    def Exec(self,sql):
        with connection() as conn:
            data = [row for row in conn.execute(sql)]
        return data

    def Save(self , props):
        values = ",".join(['{}'.format(prop) for prop in props])
        sql = """
        INSERT INTO {} values({})
        """.format(self.table , values)
        self.Exec(sql)

    def Update(self ,id):
        sql= """
        IF EXISTS (select 1 from {table_name} T where T.{id_col} = '{id}')
        BEGIN
            UPDATE {table_name}
            SET  
        end
        GO
        """.format(self.table ,self.idCol , id)
