def exec_many_str(cur, s):
    for sql in s.split('\n\n'):
        cur.execute(sql)
        cur.connection.commit()
