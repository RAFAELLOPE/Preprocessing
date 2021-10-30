import pandas as pd
import pymssql

class DatabaseAccess:
    def __init__(self, **params):
        self.ip = params["server"]
        self.db = params["db"]
        self.user = params["usr"]
        self.pwd = params["pwd"]

    def run_query(self, query: str, verbose: bool = False)-> pd.DataFrame:
        df_result = pd.DataFrame()
        conn = None
        try:
            conn = pymssql.connect(self.ip,
                                   self.user,
                                   self.pwd,
                                   self.db)
            if (verbose):
                print(query)
            df_result = pd.read_sql_query(query, conn)
        except Exception as err:
            print('CONNECTION FAILED')
            print(err)
            conn = None
        finally:
            if conn != None:
                conn.close()
        return(df_result)
