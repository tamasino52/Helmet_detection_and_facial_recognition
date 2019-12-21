import sqlite3

class DBmanager():
    def __init__(self, DBfile):
        # Connect DB
        self.conn = sqlite3.connect(DBfile)
        # Cursor from connection
        self.cur = self.conn.cursor()

    def InitDB(self):
        self.cur.execute("DROP TABLE if EXISTS 'WORKER';")

        self.cur.execute("CREATE TABLE IF NOT EXISTS 'WORKER' ("
                         "'ID'      INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"
                         "'NAME'    TEXT NOT NULL,"
                         "'RECENT'  TEXT,"
                         "'WARNINGS' INTEGER );")
        self.conn.commit()

    def InsertWorker(self, ID, name):
        ID = str(ID)

        try:
            self.cur.execute("INSERT INTO WORKER (ID, NAME, RECENT, WARNINGS) "
                             "VALUES ("+ID+", '"+name+"', CURRENT_TIMESTAMP, 0);")
            self.conn.commit()
        except sqlite3.Error as e:
            print(e.args[0])
    def DeleteAllWorker(self):
        try:
            self.cur.execute("DELETE FROM WORKER;")
            self.conn.commit()
        except sqlite3.Error as e:
            print(e.args[0])
    def DeleteWorker(self):
        try:
            self.cur.execute("DELETE FROM WORKER WHERE ID="+ID+";")
            self.conn.commit()
        except sqlite3.Error as e:
            print(e.args[0])
    def ShowAllWorker(self):
        self.cur.execute("SELECT * FROM WORKER;")
        # Data fetch
        rows = self.cur.fetchall()
        for row in rows:
            print(row)
    def GetWorkerByID(self, ID):
        ID = str(ID)

        self.cur.execute("SELECT * FROM WORKER WHERE ID=" + ID+";")
        # Data fetch
        rows = self.cur.fetchall()
        for row in rows:
            print(row)
    def GetWorkerByName(self, name):
        try:
            self.cur.execute("SELECT * FROM WORKER WHERE NAME='"+name+"';")
            # Data fetch
            rows = self.cur.fetchall()
            for row in rows:
                print(row)
        except sqlite3.Error as e:
            print(e.args[0])
    def GetIDByName(self, name):
        try:
            self.cur.execute("SELECT ID FROM WORKER WHERE NAME='"+name+"';")
            # Data fetch
            rows = self.cur.fetchall()
            for row in rows:
                return row
        except sqlite3.Error as e:
            print(e.args[0])
    def UpdateRecent(self, ID):
        ID = str(ID)

        try:
            self.cur.execute("UPDATE WORKER SET RECENT=CURRENT_TIMESTAMP WHERE ID="+ID+";")
            self.conn.commit()
        except sqlite3.Error as e:
            print(e.args[0])
    def ResetAllRecent(self):
        try:
            self.cur.execute("UPDATE WORKER SET RECENT=CURRENT_TIMESTAMP;")
            self.conn.commit()
        except sqlite3.Error as e:
            print(e.args[0])
    def AddWarnings(self, ID):
        ID = str(ID)
        try:
            self.cur.execute("UPDATE WORKER SET RECENT=CURRENT_TIMESTAMP WHERE ID="+ID+";")
            self.cur.execute("UPDATE WORKER SET WARNINGS=WARNINGS + 1 WHERE ID="+ID+";")
            self.UpdateRecent(ID)
            self.conn.commit()
        except sqlite3.Error as e:
            print(e.args[0])
    def SetWarnings(self, ID, Warnings):
        ID = str(ID)
        Warnings = str(Warnings)

        try:
            self.cur.execute("UPDATE WORKER SET WARNINGS="+Warnings+" WHERE ID="+ID+";")
            self.conn.commit()
        except sqlite3.Error as e:
            print(e.args[0])
    def SetAllWarnings(self, Warnings):
        Warnings = str(Warnings)

        try:
            self.cur.execute("UPDATE WORKER SET WARNINGS="+Warnings+";")
            self.conn.commit()
        except sqlite3.Error as e:
            print(e.args[0])