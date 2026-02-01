import os
import time
from typing import List, Dict, Optional, Any
from openai import OpenAI
import tiktoken
from .models import GrokModel, get_model_config

class GrokClient:
    """Client for interacting with Grok API with robust error handling"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        self.base_url = base_url or os.getenv("XAI_BASE_URL", "https://api.x.ai/v1")
        
        if not self.api_key:
            raise ValueError("XAI_API_KEY not found. Please set it in .env file")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        # Token counting (approximate for Grok)
        try:
            self.encoder = tiktoken.get_encoding("cl100k_base")
        except:
            self.encoder = None
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if self.encoder:
            return len(self.encoder.encode(text))
        # Rough approximation if encoder not available
        return len(text.split()) * 1.3
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: GrokModel = GrokModel.GROK_4_LATEST,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        retry_count: int = 3,
        retry_delay: float = 2.0
    ) -> Dict[str, Any]:
        """
        Send chat completion request with retry logic
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Grok model variant to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            retry_count: Number of retries on failure
            retry_delay: Delay between retries in seconds
            
        Returns:
            Dict with 'content', 'model', 'usage', and 'finish_reason'
        """
        config = get_model_config(model)
        config["temperature"] = temperature
        if max_tokens:
            config["max_tokens"] = min(max_tokens, model.max_tokens)
        
        for attempt in range(retry_count):
            try:
                response = self.client.chat.completions.create(
                    model=config["model"],
                    messages=messages,
                    temperature=config["temperature"],
                    max_tokens=config.get("max_tokens", 4096),
                    top_p=config["top_p"],
                    stream=False
                )
                
                return {
                    "content": response.choices[0].message.content,
                    "model": response.model,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    },
                    "finish_reason": response.choices[0].finish_reason
                }
                
            except Exception as e:
                if attempt < retry_count - 1:
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 1.5  # Exponential backoff
                else:
                    raise Exception(f"Failed after {retry_count} attempts: {e}")
    
    def structured_reasoning(
        self,
        prompt: str,
        context: Optional[str] = None,
        model: GrokModel = GrokModel.GROK_4_LATEST,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Perform structured reasoning with optional context
        
        Args:
            prompt: The reasoning prompt
            context: Optional context information
            model: Grok model to use
            temperature: Sampling temperature
            
        Returns:
            Dict with reasoning result and metadata
        """
        messages = []
        
        if context:
            messages.append({
                "role": "system",
                "content": f"You are an advanced research assistant. Use the following context to inform your reasoning:\n\n{context}"
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        return self.chat_completion(messages, model=model, temperature=temperature)
    
    def test_connection(self) -> bool:
        """Test if the API connection is working"""
        try:
            response = self.chat_completion(
                messages=[{"role": "user", "content": "Hello, respond with 'OK' if you receive this."}],
                max_tokens=10
            )
            return "OK" in response["content"] or len(response["content"]) > 0
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False

