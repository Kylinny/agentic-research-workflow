import json
import os
import re
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


class OfflineGrokClient:
    """Deterministic offline client for demos and local validation."""

    def __init__(self):
        self.base_url = "offline://local-heuristic"
        self.api_key = None

    def count_tokens(self, text: str) -> int:
        """Count tokens approximately without external encoders."""
        return max(1, int(len(text.split()) * 1.3))

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: GrokModel = GrokModel.GROK_4_LATEST,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        retry_count: int = 3,
        retry_delay: float = 2.0
    ) -> Dict[str, Any]:
        """Return a deterministic response shaped like the online client."""
        system_prompt = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_prompt = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")

        if "expert research planning agent" in system_prompt.lower():
            content = self._build_plan_response(user_prompt)
        elif "analyzing research results" in system_prompt.lower():
            content = self._build_analysis_response(user_prompt)
        elif "synthesizing research findings" in system_prompt.lower():
            content = self._build_synthesis_response(user_prompt)
        else:
            content = "Offline mode response."

        prompt_tokens = sum(self.count_tokens(message.get("content", "")) for message in messages)
        completion_tokens = self.count_tokens(content)

        return {
            "content": content,
            "model": f"{model.value}-offline",
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            "finish_reason": "stop",
        }

    def structured_reasoning(
        self,
        prompt: str,
        context: Optional[str] = None,
        model: GrokModel = GrokModel.GROK_4_LATEST,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Mimic the online structured reasoning API."""
        messages = []
        if context:
            messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": prompt})
        return self.chat_completion(messages, model=model, temperature=temperature)

    def test_connection(self) -> bool:
        """Offline mode is always available once imported."""
        return True

    def _build_plan_response(self, prompt: str) -> str:
        query = self._extract_query(prompt)
        query_lower = query.lower()
        tasks = []
        task_id = 1

        if any(term in query_lower for term in ["x", "twitter", "discourse", "post", "sentiment", "public"]):
            tasks.append({
                "id": task_id,
                "description": "Retrieve relevant X posts and discussion threads",
                "tool": "hybrid_retrieval",
                "parameters": {"query": query, "doc_type": "x_posts", "top_k": 10},
                "dependencies": [],
                "priority": "high"
            })
            x_task_id = task_id
            task_id += 1

            if "sentiment" in query_lower or "opinion" in query_lower:
                tasks.append({
                    "id": task_id,
                    "description": "Analyze sentiment in the retrieved social discussion",
                    "tool": "sentiment_analysis",
                    "parameters": {"posts": f"results_from_task_{x_task_id}"},
                    "dependencies": [x_task_id],
                    "priority": "high"
                })
                task_id += 1

        if any(term in query_lower for term in ["paper", "research", "study", "academic", "citation", "methodolog"]):
            tasks.append({
                "id": task_id,
                "description": "Search relevant research papers",
                "tool": "paper_search",
                "parameters": {"query": query, "limit": 10},
                "dependencies": [],
                "priority": "high"
            })
            paper_task_id = task_id
            task_id += 1

            if "citation" in query_lower or "influential" in query_lower:
                tasks.append({
                    "id": task_id,
                    "description": "Inspect citation relationships for the most relevant paper",
                    "tool": "citation_tracker",
                    "parameters": {"paper_id": f"results_from_task_{paper_task_id}", "action": "get_citations"},
                    "dependencies": [paper_task_id],
                    "priority": "medium"
                })
                task_id += 1

        if not tasks:
            tasks.append({
                "id": task_id,
                "description": "Run hybrid retrieval over the mock datasets",
                "tool": "hybrid_retrieval",
                "parameters": {"query": query, "doc_type": "x_posts", "top_k": 8},
                "dependencies": [],
                "priority": "high"
            })

        plan = {
            "reasoning": f"Offline heuristic plan for answering: {query}",
            "sub_tasks": tasks[:4],
            "expected_challenges": [
                "Mock datasets may not cover the full topic breadth",
                "Offline synthesis uses deterministic heuristics instead of live reasoning",
            ],
            "success_criteria": "Return a grounded answer with references to retrieved posts or papers."
        }
        return json.dumps(plan, indent=2)

    def _build_analysis_response(self, prompt: str) -> str:
        success_count = len(re.findall(r"Task \d+ \([^)]+\):\n(?!FAILED)", prompt))
        failure_count = len(re.findall(r"FAILED", prompt))
        quality = 8.0 if success_count >= 1 else 3.0
        completeness = 8.0 if success_count >= 1 else 2.5
        analysis = {
            "quality_score": quality,
            "completeness": completeness,
            "ambiguities": [] if success_count else ["No tool returned useful results."],
            "gaps": [] if success_count else ["Need broader retrieval coverage."],
            "needs_replanning": success_count == 0 and failure_count > 0,
            "replan_reason": "Initial tool execution failed to produce usable evidence." if success_count == 0 and failure_count > 0 else "",
            "synthesis": f"Offline analysis observed {success_count} successful task(s) and {failure_count} failed task(s)."
        }
        return json.dumps(analysis, indent=2)

    def _build_synthesis_response(self, prompt: str) -> str:
        query = self._extract_query(prompt)
        result_lines = []
        for line in prompt.splitlines():
            stripped = line.strip()
            if stripped.startswith('"title":') or stripped.startswith('"author":') or stripped.startswith('"topic":'):
                result_lines.append(stripped.strip('",'))
            if len(result_lines) >= 6:
                break

        evidence = "\n".join(f"- {line}" for line in result_lines) if result_lines else "- Retrieved evidence from the local mock datasets."

        return (
            f"Executive Summary\n"
            f"This offline run analyzed the query: {query}\n\n"
            f"Key Findings\n"
            f"{evidence}\n\n"
            f"Limitations\n"
            f"- This answer was produced in offline heuristic mode using local datasets and deterministic planning.\n"
            f"- Final judgments should be validated with a live model and broader sources.\n\n"
            f"Confidence\n"
            f"Medium confidence for demo and workflow validation; lower confidence for real-world research conclusions."
        )

    def _extract_query(self, prompt: str) -> str:
        for label in ["Research Query:", "Original Query:"]:
            if label in prompt:
                tail = prompt.split(label, 1)[1].strip()
                return tail.splitlines()[0].strip() or "Untitled query"
        return "Untitled query"
