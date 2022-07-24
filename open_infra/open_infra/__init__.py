import sys
import logging

if sys.version > '3':
    try:
        import pymysql
        from pymysql import install_as_MySQLdb
        pymysql.version_info = (1, 4, 13, "final", 0)
        install_as_MySQLdb()
    except ImportError as e:
        logging.error('Import pymysql failed, please check this package, if not required please ignore it.')
