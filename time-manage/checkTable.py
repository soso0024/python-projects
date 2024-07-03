import sqlite3

# データベースに接続
conn = sqlite3.connect("hours.db")
cur = conn.cursor()

# テーブルの内容を取得
cur.execute("SELECT * FROM hours")
rows = cur.fetchall()

# テーブルの内容を表示
print("Contents of the 'hours' table:")
for row in rows:
    print(row)

# データベースを閉じる
conn.close()
