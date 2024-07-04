import sqlite3

conn = sqlite3.connect(f"sport.sqlite3")
cur = conn.cursor()
print("Opened database successfully")


conn.execute(
    """CREATE TABLE Sport
        (DATE       DATE    NOT NULL,
        CATEGORY    TEXT    NOT NULL,
        HOURS       INT     NOT NULL,
        KIND        TEXT    NOT NULL,
        UNIQUE(DATE, CATEGORY));"""
)
print("Table created successfully")
