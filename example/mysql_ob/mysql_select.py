import mysql.connector

conn = mysql.connector.connect(
    host="127.0.0.1",
    port=2881,
    user="root@sys",
    password="",
    database="oceanbase",
)

cursor = conn.cursor()

cursor.execute("SELECT VERSION()")
print(cursor.fetchone())

cursor.execute("SELECT 1")
print(cursor.fetchone())

cursor.close()
conn.close()
