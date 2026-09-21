import mysql.connector

source = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="root",
    database="source_db",
)

target = mysql.connector.connect(
    host="localhost",
    port=2881,
    user="root@sys",
    password="",
    database="test",
)

src = source.cursor(dictionary=True)
dst = target.cursor()

src.execute("SELECT id, name, created_at FROM users")

dst.execute("""
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY,
    name VARCHAR(100),
    created_at TIMESTAMP
)
""")

for row in src.fetchall():
    dst.execute(
        """
        INSERT INTO users (id, name, created_at)
        VALUES (%s, %s, %s)
        """,
        (row["id"], row["name"], row["created_at"]),
    )

target.commit()
