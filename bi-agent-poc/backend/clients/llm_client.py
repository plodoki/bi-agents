import os
import time
import logging
import random
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class LLMClient:
    def __init__(self):
        """
        Default endpoint is OpenAI's official API, but it can be overridden
        by setting CUSTOM_OPENAI_ENDPOINT in the .env file.
        """
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.base_url = os.getenv(
            "CUSTOM_OPENAI_ENDPOINT", "https://api.openai.com/v1")

        # Set your default model here or let your agent pass it in dynamically
        self.default_model = "gpt-4o-mini-2024-07-18"

        # Validate we have a key
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment.")

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def call_chat_completion(self,
                             messages: list,
                             model: str = None,
                             temperature: float = 0.8,
                             max_retries: int = 3,
                             backoff_factor: float = 1.5) -> str:
        """
        Make a ChatCompletion request with basic retry logic.
        :param messages: A list of dicts with roles (system|user|assistant) and content.
        :param model: Which model to use (default if None).
        :param temperature: Controls the randomness of the output.
        :param max_retries: How many times to retry in case of error.
        :param backoff_factor: Controls the incremental sleep between retries.
        :return: The content of the assistant's response.
        """
        if not model:
            model = self.default_model

        attempt = 0
        while attempt < max_retries:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature
                )
                logger.debug(f"LLM response: {
                             response.choices[0].message.content.strip()}")
                return response.choices[0].message.content.strip()
            except OpenAIError as e:
                logger.warning(f"API error: {e}")
                attempt += 1
                if attempt >= max_retries:
                    raise
                sleep_time = backoff_factor * attempt + random.uniform(0, 1)
                logger.info(f"Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
