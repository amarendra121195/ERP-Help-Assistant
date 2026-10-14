import pyodbc

from app.core import config


def run_query(sql, params=()):
    with pyodbc.connect(config.SQL_SERVER_CONN, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
