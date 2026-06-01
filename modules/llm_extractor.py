from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from config import Config
from utils.logger import logger
import json

class LLMExtractor:
    def __init__(self, api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.0,
            google_api_key=api_key,
            api_version="v1"
        )
        self.output_parser = JsonOutputParser()

    def extract_structured_data(self, text: str) -> Dict[str, Any]:
        """Use LLM to extract structured data from unstructured text."""
        if not text:
            return {}

        logger.info("Using LLM fallback for contact extraction...")
        
        prompt = ChatPromptTemplate.from_template(
            "Extract business contact details from the following web page content. "
            "Return the output as a JSON object with the following keys: "
            "business_name, email, phone, address, category. "
            "If a value is not found, leave it empty. Return ONLY the JSON.\n\n"
            "Content:\n{text}"
        )

        try:
            chain = prompt | self.llm | self.output_parser
            result = chain.invoke({"text": text[:4000]})
            return result
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return {}
