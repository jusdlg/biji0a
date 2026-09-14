import _sqlite3

conn = _sqlite3.connect("blog.db")
cur = conn.cursor()

# 用户表
cur.execute('''create table if not exists user(
id integer primary key autoincrement,
name text,
password text
)''')

#博客表，新增 publish_time
cur.execute('''create table if not exists blog(
id integer primary key autoincrement,
title text,
content text,
uid integer,
publish_time datetime
)''')

#给旧数据库自动补充时间字段，不会重复报错
try:
    cur.execute("ALTER TABLE blog ADD COLUMN publish_time DATETIME")
except Exception:
    pass

conn.commit()
cur.execute("select * from user")
v=cur.fetchall()
print(v)
conn.close()