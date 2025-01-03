import os
import json


class RAGManager:
    def __init__(self, knowledge_base_dir: str = "knowledge_base/tables"):
        """
        Initialize the RAGManager with a path to the knowledge base directory.
        """
        self.knowledge_base_dir = knowledge_base_dir
        # {table_name: { 'table_name': str, 'columns': [...], 'table_description': str }}
        self._tables_cache = {}
        self._load_tables()

    def _load_tables(self):
        """
        Private method to load all JSON files in the knowledge_base_dir folder
        and store them in a cache for quick lookups.
        """
        if not os.path.exists(self.knowledge_base_dir):
            return  # or raise an exception if folder must exist

        for file_name in os.listdir(self.knowledge_base_dir):
            if file_name.endswith(".json"):
                file_path = os.path.join(self.knowledge_base_dir, file_name)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        table_data = json.load(f)
                        table_name = table_data.get("table_name")
                        if table_name:
                            self._tables_cache[table_name] = table_data
                except (json.JSONDecodeError, OSError) as e:
                    # Log or handle file read/parse errors
                    print(f"Error reading {file_path}: {e}")

    def get_all_tables_info(self):
        """
        Return a list of dictionaries, each containing the table name and description.
        Example output:
        [
          {
            "table_name": "sales",
            "table_description": "The 'sales' table contains ..."
          },
          ...
        ]
        """
        result = []
        for table_data in self._tables_cache.values():
            result.append({
                "table_name": table_data.get("table_name"),
                "table_description": table_data.get("table_description", "")
            })
        return result

    def get_table_attribute(self, table_name: str, attribute_name: str):
        """
        Given a table name and an attribute (column) name, return the metadata for that column.
        If the column or table is not found, return None or raise an exception.
        """
        table_data = self._tables_cache.get(table_name)
        if not table_data:
            return None

        columns = table_data.get("columns", [])
        for col in columns:
            if col.get("name") == attribute_name:
                return col
        return None

    def get_table_schema(self, table_name: str):
        """
        Return the entire columns array for a given table name.
        If the table is not found, return None or raise an exception.
        """
        table_data = self._tables_cache.get(table_name)
        if not table_data:
            return None
        return table_data.get("columns")

    def get_key_value_pair(self, table_name: str, key: str):
        """
        Retrieve the value for a given key from the table data.
        If the key does not exist, return None or raise an exception.
        """
        table_data = self._tables_cache.get(table_name)
        if not table_data:
            return None

        # Check if the key exists in the table data
        if key in table_data:
            return {key: table_data[key]}
        return None

    def get_tables_info(self, table_names: list):
        """
        Retrieve the table information for a list of table names.
        If a table does not exist, it will not be included in the result.
        """
        result = {}
        for table_name in table_names:
            table_info = self._tables_cache.get(table_name)
            if table_info:
                result[table_name] = table_info
        return json.dumps(result)
