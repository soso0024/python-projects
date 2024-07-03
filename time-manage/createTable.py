import sqlite3

conn = sqlite3.connect(f"hours.sqlite3")
cur = conn.cursor()
print("Opened database successfully")


conn.execute(
    """CREATE TABLE hours
        (DATE       DATE    NOT NULL,
        CATEGORY    TEXT    NOT NULL,
        HOURS       INT     NOT NULL,
        PART        TEXT    NOT NULL);"""
)
print("Table created successfully")
