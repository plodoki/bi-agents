class SQLGeneratorAgent:
    def generate_sql(self, user_query: str, rag_context: dict) -> str:
        # Use LLM or rule-based approach to convert query -> SQL
        # Example stub
        return "SELECT * FROM orders WHERE amount > 100"
