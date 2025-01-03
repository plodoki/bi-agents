import json
import logging
from typing import Dict, List, Tuple, Union

from utils.prompts import get_prompt_query_hints, get_prompt_suggested_tables

logger = logging.getLogger(__name__)


class QueryHelperAgent:
    """
    The QueryHelperAgent uses an LLM (Language Model) and RAG (Retrieval-Augmented Generation)
    manager to determine which tables are needed to fulfill a user query and to provide
    high-level instructions (query hints) on forming an SQL query.

    The generate_query_hints method orchestrates:
    1. Identifying relevant tables from the knowledge base.
    2. Generating a query outline (column usage, joins, filters).
    3. Collecting any open questions if the query is ambiguous or missing information.
    """

    def __init__(self, rag_manager, llm_client):
        """
        Initializes the QueryHelperAgent.

        :param rag_manager: An instance responsible for managing the knowledge base.
        :param llm_client:   An LLM client to send chat completion requests.
        """
        self.rag_manager = rag_manager
        self.llm_client = llm_client

    def generate_query_hints(self, user_query: str) -> Dict[str, Union[str, List[str]]]:
        """
        Main entry point to gather query hints.

        :param user_query: The user's natural language query.
        :return: A dictionary containing:
                 - 'user_query' (str): Echoes the original user query.
                 - 'suggested_tables' (list): Tables deemed relevant by the LLM.
                 - 'query_hints' (str): A step-by-step outline of how to form the SQL query.
                 - 'open_questions' (list): Clarifications required for ambiguous or incomplete queries.
        """
        available_tables = self.rag_manager.get_all_tables_info()
        payload = {
            "user_query": user_query,
            "available_tables": available_tables
        }

        suggested_tables = self._get_suggested_tables(payload)
        if suggested_tables:
            query_hints, open_questions = self._get_query_hints(
                user_query, suggested_tables)
        else:
            query_hints = ""
            open_questions = []

        return {
            "user_query": user_query,
            "suggested_tables": suggested_tables,
            "query_hints": query_hints,
            "open_questions": open_questions
        }

    def _get_suggested_tables(self, payload: dict) -> List[str]:
        """
        Invokes the LLM to determine which tables from the knowledge base
        are likely required for the user's query.

        :param payload: A dictionary containing the user query and a list
                        of available tables.
        :return: A list of suggested table names.
        """
        developer_prompt = get_prompt_suggested_tables()
        messages = [
            {"role": "developer", "content": developer_prompt},
            {"role": "user", "content": json.dumps(payload, indent=2)}
        ]
        logger.debug("Table-suggestion messages: %s", messages)

        try:
            response = self.llm_client.call_chat_completion(messages=messages)
            response_dict = json.loads(response)
            suggested_tables = response_dict.get("tables", [])
            logger.info("Suggested tables: %s", suggested_tables)
        except json.JSONDecodeError as exc:
            logger.error(
                "Error parsing LLM response for suggested tables: %s", exc)
            suggested_tables = []

        return suggested_tables

    def _get_query_hints(self, user_query: str, suggested_tables: List[str]) -> Tuple[str, List[str]]:
        """
        Once tables are identified, calls the LLM again to produce a
        high-level instruction set (query hints) and capture any open questions.

        :param user_query: The user's natural language query.
        :param suggested_tables: List of tables identified as relevant by the LLM.
        :return: A tuple of (query_hints, open_questions).
        """
        table_context_json = self.rag_manager.get_tables_info(suggested_tables)
        prompt_generate_query_hints = get_prompt_query_hints()

        user_prompt = {
            "user_query": user_query,
            "table_context": table_context_json
        }

        messages = [
            {"role": "developer", "content": prompt_generate_query_hints},
            {"role": "user", "content": json.dumps(user_prompt, indent=2)}
        ]
        logger.debug("Query-hint messages: %s", messages)

        query_hints = ""
        open_questions = []

        try:
            response = self.llm_client.call_chat_completion(
                messages=messages)
            response_dict = json.loads(response)
            logger.debug("Query-hint response: %s", response_dict)
            query_hints = response_dict.get("query_description", "")
            open_questions = response_dict.get("open_questions", [])
        except json.JSONDecodeError as exc:
            logger.error("Error parsing LLM response for query hints: %s", exc)

        return query_hints, open_questions
