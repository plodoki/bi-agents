import os
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import FastAPI
from agents.chatbot_agent import ChatBotAgent
from agents.sql_generator_agent import SQLGeneratorAgent
from agents.sql_validation_agent import SQLValidationAgent
from agents.query_helper_agent import QueryHelperAgent
from rag.rag_manager import RAGManager
from agents.data_analyzer import DataAnalyzer
from clients.duckdb_client import DuckDBDataRetrievalClient
from clients.postgres_client import PostgresClient
from clients.llm_client import LLMClient
import logging

# Load environment variables from .env
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI(debug=True)

# Initialize Agents and Clients
rag_manager = RAGManager()
llm_client = LLMClient()
chatbot_agent = ChatBotAgent()
sql_agent = SQLGeneratorAgent()
query_generator_agent = QueryHelperAgent(rag_manager, llm_client)
validation_agent = SQLValidationAgent()
data_analyzer = DataAnalyzer()


# Fetch DB connection info from environment
POSTGRES_CONN_INFO = {
    "host": os.getenv("POSTGRES_HOST"),
    "database": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "port": int(os.getenv("POSTGRES_PORT"))
}
DB_BACKEND = os.getenv("DB_BACKEND", "duckdb")

if DB_BACKEND == "postgres":
    data_retrieval_client = PostgresClient()
    data_retrieval_client.initialize_connection(POSTGRES_CONN_INFO)
else:
    DATA_DIR = "table_data"  # where .csv or .parquet files are stored
    data_retrieval_client = DuckDBDataRetrievalClient(DATA_DIR)


class QueryRequest(BaseModel):
    query: str


@app.post("/query")
def query_data(request: QueryRequest):

    # 1. ChatBotAgent: refine user query
    refined_query = chatbot_agent.get_user_query(request.query)

    # 2. QueryHelper Agents identifies which tables to use
    query_hints = query_generator_agent.generate_query_hints(refined_query)

    return {
        "refined_query": refined_query,
        "query_hints": query_hints
    }

    if (1 == 2):

        # 3. SQLAgent: generate SQL
        sql_query = sql_agent.generate_sql(refined_query, query_hints)

        # 4. SQLValidationAgent: validate SQL
        validation_result = validation_agent.validate_sql(
            refined_query, sql_query, query_hints)
        if not validation_result["is_correct"]:
            return {
                "status": "error",
                "message": validation_result["feedback"]
            }

        # 5. DataRetrievalAgent: run query
        data = data_retrieval_client.run_query(validation_result["sql_query"])

        # 6. DataAnalyzer: produce the final answer
        answer = data_analyzer.analyze_and_respond(
            data, refined_query)

        return {"answer": answer}


@app.get("/tables")
def list_tables():
    """
    Endpoint to list tables from the knowledge base.
    """
    return rag_manager.get_all_tables_info()


@app.get("/tables/{table_name}/schema")
def get_table_schema(table_name: str):
    """
    Endpoint to get the schema for a specific table.
    """
    schema = rag_manager.get_table_schema(table_name)
    if not schema:
        return {"error": f"Table '{table_name}' not found"}
    return schema


@app.get("/tables/{table_name}/columns/{attribute_name}")
def get_table_column(table_name: str, attribute_name: str):
    """
    Endpoint to get a specific column's metadata from a table.
    """
    column_data = rag_manager.get_table_attribute(table_name, attribute_name)
    if not column_data:
        return {"error": f"Column '{attribute_name}' not found in table '{table_name}'"}
    return column_data


@app.get("/tables/{table_name}/key/{key}")
def get_table_key_value_pair(table_name: str, key: str):
    """
    Endpoint to get a specific metadata field for a table.
    """
    value = rag_manager.get_key_value_pair(table_name, key)
    if not value:
        return {"error": f"Key '{key}' not found in table '{table_name}'"}
    return value


@app.post("/run-sql")
def run_sql_query(request: QueryRequest):
    """
    Endpoint to directly run a SQL query using the data_retrieval_client.
    """
    try:

        cursor = data_retrieval_client.db.execute(request.query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        # Option A: Return columns + rows as arrays
        return {
            "columns": columns,
            "data": rows
        }

        # Option B: Return a list of dicts
        # data_as_dicts = [dict(zip(columns, row)) for row in rows]
        # return {"data": data_as_dicts}

    except Exception as e:
        return {"error": str(e)}
