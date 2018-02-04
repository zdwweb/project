import pymysql
from DBUtils.PooledDB import PooledDB
import collections
import itertools

conn=None

def connection(user, host, passwd, db, charset="utf8"):
    global conn
    pool = PooledDB(pymysql,
                    maxconnections=5,
                    user=user,
                    host=host,
                    passwd=passwd,
                    db=db,
                    charset=charset,
                    )
    try:
        conn = pool.connection()
    except Exception as e:
        print(e)
    else:
        print("success")

class dbconn(object):

    def __init__(self):
        self._conn=conn
        self._cursor=self._conn.cursor(cursor=pymysql.cursors.DictCursor)



    def _close(self):
        self._cursor.close()
        self._conn = None

    def __del__(self):
        if self._conn:
            self._close()

    def __enter__(self):
        return self

    def __exit__(self, etyp, eval, tb):
        self._close()

    def _close(self):
        self._cursor.close()
        self._conn = None

    def __iter__(self):
        self._cursor.__iter__()

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    @property
    def rowcount(self):
        return self._cursor.rowcount

    @property
    def rownumber(self):
        return self._cursor.rownumber

    def execute(self, operation, parameters=None):
        return self._cursor.execute(operation, parameters)

    def fetchall(self):

        items=self._cursor.fetchall()
        return list([tuple(item.values()) for item in items])

    def fetchall_dicts(self):

        return self._cursor.fetchall()

    def fetchone(self):
        item=self._cursor.fetchone()
        return list(item.values())

    def fetchone_dict(self):
        return self._cursor.fetchone()


def main():
    try:
        connection(user='',
                   host='',
                   passwd='',
                   db='')
        with dbconn() as cur:
            count=cur.execute("select * from cstm")
            item=cur.fetchall()
            print(item)
            print(count)

    except Exception as e:
        print(e)
    finally:
        print("")
     
main()
        
