# -*- coding: utf-8 -*-

import collections
import itertools

# 注册字符串缺省类型为unicode
import psycopg2.extensions
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

import psycopg2.extras
import psycopg2.pool

_pg_conn_pools = {}

def register_dsn(dsn, pool_name=None, minconn=1, maxconn=20):
    '''注册数据库连接字符串'''
    pool = psycopg2.pool.ThreadedConnectionPool(
        minconn=minconn, maxconn=maxconn, dsn=dsn)
    _pg_conn_pools[pool_name] = pool


def _get_connection_pool(name=None):
    if name not in _pg_conn_pools :
        s = "You should register a dsn at first for '%s' pool"
        s %= (name if name else 'default')
        raise ConnectionError(s)

    return _pg_conn_pools[name]

class ConnectionError(LookupError):
    pass

class SimpleDataCursor(object):

    def __init__(self, pool_name=None, autocommit=True):

        self._pool = _get_connection_pool(pool_name)
        self._conn = self._pool.getconn()
        self._conn.autocommit = autocommit
        self._cursor = self._conn.cursor(
        cursor_factory=psycopg2.extras.NamedTupleCursor)
            
    def __del__(self):
        if self._conn:
            self._close()
        
    def __enter__(self):
        return self

    def __exit__ (self, etyp, eval, tb):
        self._close()
        
    def _close(self):
        self._cursor.close()
        self._pool.putconn(self._conn)
        self._conn = None
    
    def __iter__(self):
        self._cursor.__iter__()

    @property 
    def rowcount(sefl):
        self._cursor.rowcount

    @property 
    def rownumber(sefl):
        self._cursor.rowcount

    def execute(self, operation, parameters=()):
        self._cursor.execute(operation, parameters)
        return self._cursor.execute(operation, parameters)

    def fetchall(self):
        ''' 获取所有数据，将各条记录转换成由元组(namedtuple)组成的列表'''
        return self._cursor.fetchall()

    

    def fetchone(self):
        ''' 获取第一行的数据'''
        return self._cursor.fetchone()

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()
