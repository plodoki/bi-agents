import duckdb
import os


class DuckDBDataRetrievalClient:
    def __init__(self, data_dir: str):
        """
        Initialize an in-memory DuckDB connection and create tables for
        all CSV or Parquet files found in `data_dir`.
        """
        self.db = duckdb.connect()
        self.data_dir = data_dir
        self._create_tables_from_files()

    def _create_tables_from_files(self):
        """
        Iterate over all CSV/Parquet files in `self.data_dir` and create (or replace)
        DuckDB tables matching the file names (minus extension).
        """
        for file_name in os.listdir(self.data_dir):
            file_path = os.path.join(self.data_dir, file_name)
            extension = os.path.splitext(file_name)[1].lower()

            if extension == ".csv":
                # For CSV files, use DuckDB's read_csv_auto
                table_name = os.path.splitext(file_name)[0]
                self.db.execute(f"""
                    CREATE OR REPLACE TABLE {table_name} AS
                    SELECT * FROM read_csv_auto('{file_path}');
                """)

            elif extension == ".parquet":
                # For Parquet files, use DuckDB's parquet_scan
                table_name = os.path.splitext(file_name)[0]
                self.db.execute(f"""
                    CREATE OR REPLACE TABLE {table_name} AS
                    SELECT * FROM parquet_scan('{file_path}');
                """)

    def run_query(self, sql_query: str):
        """
        Execute the given SQL query against the in-memory DuckDB instance,
        which already has all CSV/Parquet-based tables loaded.
        """
        return self.db.execute(sql_query).fetchall()
