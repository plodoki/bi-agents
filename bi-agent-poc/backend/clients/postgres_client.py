import psycopg2


class PostgresClient:
    def __init__(self):
        self.conn = None

    def initialize_connection(self, conn_info: dict):
        self.conn = psycopg2.connect(**conn_info)

    def run_query(self, sql_query: str):
        with self.conn.cursor() as cur:
            cur.execute(sql_query)
            rows = cur.fetchall()
        return rows
