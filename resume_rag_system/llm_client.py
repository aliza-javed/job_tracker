"""
llm_client.py
-------------
Gemini LLM client for RAG queries.
"""

import os
import logging

logger = logging.getLogger(__name__)


class GeminiLLMClient:
    """Gemini API client for answering questions."""
    
    def __init__(self):
        self.api_key = os.getenv('AQ.Ab8RN6LwZpemwAgBxl97FwYOj0LdYhLuD9hzBay2zJiC5pLP3Qa')
        self.model = None
        
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not set in environment")
            return
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            logger.info("Gemini client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
    
    def query(self, question):
        """Send question to Gemini and return answer."""
        if not self.model:
            return "LLM not available. Please check API key."
        
        try:
            prompt = f"""You are a career coach. Answer this job-related question concisely.
            
Question: {question}

Answer in 3-5 sentences maximum. Focus on actionable advice."""
            
            response = self.model.generate_content(prompt)
            return response.text
        
        except Exception as e:
            logger.error(f"Gemini query failed: {e}")
            return f"Error: {str(e)}"