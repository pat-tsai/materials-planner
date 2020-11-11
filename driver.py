import pyodbc

# ------------------------------------------queries------------------------------------------
# query to find SKU corresponding to most recent BOM revision
sql = """
SELECT i.ima_itemno, i.ima_rev, i.ima_type, b.bom_itemno, b.bom_compitem, b.bom_rev, b.bom_qty
FROM ima as i
LEFT JOIN bom as b
	ON i.ima_itemno = b.bom_itemno
WHERE i.ima_rev = b.bom_rev
	AND i.ima_itemno LIKE ?;
"""

# query to check if a sub-component BOM exists
sql2 = """
SELECT i.ima_itemno, b.bom_itemno
FROM ima as i
LEFT JOIN bom as b
	ON i.ima_itemno = b.bom_itemno
WHERE i.ima_itemno LIKE ?;
"""

sql_ima_type = """
SELECT ima_type 
FROM ima
WHERE ima_itemno LIKE ?;
"""

sql_oh_qty = """
SELECT i.ima_oh, i.ima_netoh, i.ima_itemno,
	   p.pos_qtyord, p.pos_qtyacc, p.pos_confirmation, p.pos_lmdte
FROM ima as i
LEFT JOIN pos as p
	ON i.ima_itemno = p.pos_itemno
	AND p.pos_ordsts  < 8
WHERE i.ima_itemno LIKE ?;
"""

sql_get_quote_items ="""
SELECT * FROM ZSCRM_QUOTE_READ_ITEM 
WHERE ORDER_NUM LIKE ?;
"""

sql_getCrmQuote = '''
SELECT ORDER_NUM, ASM_TYPE, SOLD_TO_ID, SOLD_TO_NAME1,
	   SHIP_TO_ID, SHIP_TO_NAME1, SHIP_TO_STREET
FROM ZSCRM_QUOTE_READ_HEADER
WHERE SALES_ORG = '1889'
	AND ORDER_NUM LIKE ?;
'''
# -------------------------------------------------------------------------------------------

class Sqlconnection():

    def __init__(self, login_user):
        if login_user == 1:
            self.sqlserver = 'mpserver6'
            self.sqlusername = 'jennifert'
            self.sqlpassword = 'Pt983!2020'
            self.sqldatabase = 'superdb'
        if login_user == 2:
            self.sqlserver = 'USSTAGEDB01\\USSTAGESQL'
            self.sqlusername = 'ken.tsai'
            self.sqlpassword = 'kT6900*()'
            self.sqldatabase = 'SAPSTAGEData'

    def __connect__(self):
        try:
            self.con = pyodbc.connect(
                'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + self.sqlserver + ';DATABASE=' + self.sqldatabase + ';UID=' + self.sqlusername + ';PWD=' + self.sqlpassword)
            self.cur = self.con.cursor()
            # print ("Connection to SQL server success: %s, %s" % (self.sqlserver, self.sqldatabase))

        except:
            LogError("Connection to SQL server failed: %s, %s" % (self.sqlserver, self.sqldatabase))

    def __disconnect__(self):
        # print("SQL CLosed....")
        self.con.close()

    def fetch(self, sql):
        self.__connect__()
        self.cur.execute(sql)
        result = self.cur.fetchall()
        self.__disconnect__()
        return result

    # This SP function  does npot have return OUTPUT value yet??? 4/1/2020
    def fetchSP(self, sql):
        self.__connect__()
        self.cur.execute(sql)
        result = self.cur.fetchall()
        self.__disconnect__()
        return result

    def fetchDict(self, sql):
        self.__connect__()
        self.cur.execute(sql)
        # result = self.cur.fetchall()
        desc = self.cur.description
        column_names = [col[0] for col in desc]
        result = [dict(zip(column_names, row)) for row in self.cur.fetchall()]
        self.__disconnect__()
        return result

    def fetchSPP(self, sql, params):
        self.__connect__()
        self.cur.execute(sql, params)
        result = self.cur.fetchall()
        self.__disconnect__()
        return result

    def fetchSPPDict(self, sql, params):
        self.__connect__()
        self.cur.execute(sql, params)
        desc = self.cur.description
        column_names = [col[0] for col in desc]
        result = [dict(zip(column_names, row)) for row in self.cur.fetchall()]
        self.__disconnect__()
        return result

    def execute(self, sql):
        self.__connect__()
        self.cur.execute(sql)
        self.__disconnect__()

