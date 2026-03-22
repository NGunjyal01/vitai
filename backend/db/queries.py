# db/queries.py
from db.connection import get_conn, put_conn

def execute_query(query, params=None):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if cur.description:
                result = cur.fetchall()
            else:
                result = None
            conn.commit()
            return result
    finally:
        put_conn(conn)