#!/usr/bin/python3

import pymysql

print("Content-Type: text/html")
print()

conn = pymysql.connect(
        db='testdb',
        user='root',
        passwd='yr240904_',
        host='localhost')
c = conn.cursor()


c.execute("SELECT * FROM test;")
for i in c:
    print(i)
