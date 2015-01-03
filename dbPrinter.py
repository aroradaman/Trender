path = r'C:\python\trend\Data.db'
import sqlite3
con = sqlite3.connect(path)
con.text_factory = str
cur = con.cursor()
cur.execute('select * from Data')
L = cur.fetchall()
for i in L :
    print i[1]
