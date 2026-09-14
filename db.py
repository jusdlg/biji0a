import sqlite3

def query_sql(sql, args=()):
    conn = sqlite3.connect("blog.db")
    cur = conn.cursor()
    cur.execute(sql, args)
    res = cur.fetchall()
    conn.close()
    return res

def exec_sql(sql, args=()):
    conn = sqlite3.connect("blog.db")
    cur = conn.cursor()
    cur.execute(sql, args)
    conn.commit()
    conn.close()