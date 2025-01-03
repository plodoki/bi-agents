# Agentic Data Query App (WIP)

Welcome to the **Agentic Data Query App** repository! This project aims to provide an AI-assisted application for generating and validating SQL queries against your dataset(s), plus optionally analyzing and refining results. It uses multiple specialized "agents" and various backend clients to accomplish these tasks.

> **Note**: This project is a **work in progress**. Many features are still incomplete or under active development.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [Setup & Installation](#setup--installation)
5. [Environment Variables](#environment-variables)
6. [Running the App](#running-the-app)
7. [Usage & Endpoints](#usage--endpoints)
8. [Agents Explained](#agents-explained)
9. [Clients Explained](#clients-explained)
10. [Development Status & Roadmap](#development-status--roadmap)
11. [Contributing](#contributing)
12. [License](#license)

---

## Overview

This repository houses a FastAPI-based server that leverages multiple "agent" modules to handle various natural language and SQL query tasks. The primary idea is to let users enter natural language queries, which get processed by a pipeline of agents to refine the query, identify the relevant tables, generate SQL, validate it, run it against a chosen database, and then analyze the results. 

By default, it can interact with either:
- A **DuckDB** in-memory database (sourcing data from CSV or Parquet files),
- Or a **PostgreSQL** database, using credentials specified via environment variables.

An **LLM** (Language Model) client is also used to help with some tasks like refining queries and table selection.

---

## Features

- **Multiple Agents**:
  - **ChatBotAgent**: Takes user input and refines it.
  - **QueryHelperAgent**: Proposes relevant tables and query hints.
  - **SQLGeneratorAgent**: (Stub/Example) converts natural language into SQL.
  - **SQLValidationAgent**: (Stub/Example) validates the generated SQL.
  - **DataAnalyzer**: Analyzes query results and produces a final answer.

- **Data Retrieval**:
  - **DuckDB** or **Postgres** integration for running SQL queries.
  - Simple architecture for adding new database clients.

- **RAG (Retrieval-Augmented Generation)**:
  - Maintains a small "knowledge base" describing table schemas, columns, and sample data to help the agents produce better queries.

- **Endpoints** (FastAPI):
  - `/query` – Receives a natural language query, returns refined query & table suggestions.
  - `/run-sql` – Directly run a SQL query on the DB.
  - Various `/tables` endpoints to explore the knowledge base schema.

- **Modular & Extensible** design for experimentation.

---

## Project Structure

Below is the general file tree (folders shown with a trailing slash):

```
.
├── backend/
│   └── main.py             # FastAPI entry point
├── clients/
│   ├── postgres_client.py  # Postgres client to connect & run queries
│   ├── duckdb_client.py    # DuckDB client to load CSV/Parquet & run queries
│   └── llm_client.py       # LLM client for calling an LLM (OpenAI, etc.)
├── agents/
│   ├── chatbot_agent.py         # Minimal agent refining user input
│   ├── sql_validation_agent.py  # Stub for SQL validation
│   ├── sql_generator_agent.py   # Stub for generating SQL
│   ├── data_analyzer.py         # Stub for analyzing final data
│   └── query_helper_agent.py    # Agent that suggests tables & query outline
├── utils/
│   ├── prompts.py  # Prompt templates for the LLM
│   └── utils.py    # Placeholder utilities
├── rag/
│   └── rag_manager.py  # Manager that loads knowledge base info & merges context
├── table_data/
│   └── sales.csv       # Example data loaded into DuckDB
└── knowledge_base/
    └── tables/
        └── sales.json  # Table metadata used by RAGManager
```

### Notable Files

- **`main.py`**: Initializes the FastAPI app, loads environment variables, instantiates all agents, configures DB connections, and defines endpoints.
- **`rag_manager.py`**: Loads table metadata (JSON files) and provides methods to retrieve relevant schema info.
- **`llm_client.py`**: Example client that integrates with OpenAI (or a custom endpoint) for ChatCompletion calls.
- **`sales.csv`** & **`sales.json`**: Example data and metadata describing a supermarket sales table.

---

## Setup & Installation

1. **Clone the repo**:
   ```bash
   git clone https://github.com/plodoki/bi-agents.git
   cd agentic-data-query-app
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   > The `requirements.txt` will include packages like `fastapi`, `uvicorn`, `python-dotenv`, `openai`, `psycopg2` (for Postgres), etc.

4. **Configure environment variables** (see [Environment Variables](#environment-variables)).

---

## Environment Variables

Create a `.env` file in the root (or wherever you run `main.py`) containing variables like:

```bash
OPENAI_API_KEY=YOUR_API_KEY
CUSTOM_OPENAI_ENDPOINT= # Optionally set a custom endpoint
DB_BACKEND=duckdb       # or "postgres"

POSTGRES_HOST=localhost
POSTGRES_DB=mydatabase
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_PORT=5432
```

- **`DB_BACKEND`** determines which database client is used (`duckdb` or `postgres`). 
- **`OPENAI_API_KEY`** is required if you plan to use the default LLM client (OpenAI).

---

## Running the App

Run the FastAPI server with Uvicorn:

```bash
uvicorn backend.main:app --reload
```

The server should be accessible at [http://127.0.0.1:8000](http://127.0.0.1:8000).

> **Note**: If you’re using a `POSTGRES_BACKEND`, ensure your Postgres server is running and the credentials in `.env` match.

---

## Usage & Endpoints

### 1. `/query` (POST)
- **Body**: 
  ```json
  {
    "query": "Show me total sales by product line"
  }
  ```
- **Description**: 
  1. Refines user query with **ChatBotAgent** (placeholder in current WIP).
  2. Uses **QueryHelperAgent** to suggest relevant tables and produce an outline.

- **Response**:
  ```json
  {
    "refined_query": "Show me total sales by product line",
    "query_hints": {
      "user_query": "...",
      "suggested_tables": [...],
      "query_hints": "...",
      "open_questions": [...]
    }
  }
  ```

### 2. `/run-sql` (POST)
- **Body**:
  ```json
  {
    "query": "SELECT * FROM sales LIMIT 5;"
  }
  ```
- **Description**: Runs the provided SQL directly against the DB (DuckDB/Postgres).
- **Response**:
  ```json
  {
    "columns": ["Invoice ID", "Branch", "City", ...],
    "data": [
      ["750-67-8428","A","Yangon",...],
      ...
    ]
  }
  ```

### 3. `/tables` (GET)
- Returns a list of table names & descriptions from the knowledge base.

### 4. `/tables/{table_name}/schema` (GET)
- Returns the schema (columns array) of the specified table.

### 5. `/tables/{table_name}/columns/{attribute_name}` (GET)
- Returns the column metadata for a specific column in a table.

### 6. `/tables/{table_name}/key/{key}` (GET)
- Returns a specific key-value pair from the table’s metadata (e.g., "table_description").

---

## Agents Explained

1. **ChatBotAgent**
   - Minimal placeholder that currently echoes user input. Intended for expansions like:
     - Query clarification
     - Additional user instructions
     - Step-by-step conversation flow

2. **QueryHelperAgent**
   - Identifies which tables/columns are relevant to a user’s query.
   - Produces high-level instructions (query hints) on how to form the SQL (like which columns to group by, how to filter, etc.).

3. **SQLGeneratorAgent**
   - (Stub) Takes the user query + table context to build SQL. Currently returns a hardcoded example.

4. **SQLValidationAgent**
   - (Stub) Checks the correctness of the generated SQL. Could be expanded to parse or run `EXPLAIN` queries.

5. **DataAnalyzer**
   - (Stub) Analyzes query results and returns a user-friendly summary.

---

## Clients Explained

1. **DuckDBDataRetrievalClient**:
   - Creates an in-memory DuckDB instance.
   - Scans the `table_data/` directory for CSV or Parquet files, creating or replacing tables.
   - Runs queries entirely in-memory.

2. **PostgresClient**:
   - Connects to an existing PostgreSQL instance using `psycopg2`.
   - Runs queries directly on a live Postgres DB.

3. **LLMClient**:
   - Interacts with the OpenAI API (or a custom endpoint) for ChatCompletions.
   - Includes retry logic and can be configured with a custom model or temperature.

---

## Development Status & Roadmap

- **Current State**: 
  - Basic scaffolding for agents is in place. 
  - DuckDB & Postgres connections work.
  - RAG Manager loads table metadata from JSON.
  - Some endpoints are just stubs or partial.

- **Upcoming**:
  - Expand `SQLGeneratorAgent` to dynamically generate queries using LLM or rule-based logic.
  - Improve `SQLValidationAgent` for robust syntax/semantic checks.
  - Flesh out `DataAnalyzer` for advanced data summarization or visualizations.
  - Add more robust error handling and logging.
  - Improve front-end (if included) for a more user-friendly UI.

---

## License

[Apache License](LICENSE) – This project is open-source under the Apache License, Version 2.0.


