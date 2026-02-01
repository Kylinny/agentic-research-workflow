"""
Agent planner for task decomposition and planning
"""
import json
from typing import Dict, Optional
from grok import GrokClient, GrokModel
from grok.prompts import PLANNER_SYSTEM_PROMPT, get_planning_prompt, get_replanning_prompt

class AgentPlanner:
    """Plans and decomposes research tasks"""
    
    def __init__(self, grok_client: GrokClient, model: GrokModel = GrokModel.GROK_4_LATEST):
        self.grok = grok_client
        self.model = model
    
    def create_plan(self, query: str, context: str = "") -> Dict:
        """
        Create an execution plan for a research query
        
        Args:
            query: The research query
            context: Optional context from previous steps
            
        Returns:
            Dict with plan structure
        """
        prompt = get_planning_prompt(query, context)
        
        messages = [
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.grok.chat_completion(
                messages=messages,
                model=self.model,
                temperature=0.7
            )
            
            # Parse JSON response
            content = response["content"]
            plan = self._extract_json(content)
            
            if not plan:
                # Fallback if JSON parsing fails
                plan = self._create_fallback_plan(query)
            
            # Validate plan structure
            plan = self._validate_plan(plan)
            
            return {
                "success": True,
                "plan": plan,
                "raw_response": content,
                "model_used": response["model"]
            }
            
        except Exception as e:
            print(f"Planning error: {e}")
            return {
                "success": False,
                "error": str(e),
                "plan": self._create_fallback_plan(query)
            }
    
    def replan(self, original_plan: Dict, issue: str, current_results: str) -> Dict:
        """
        Create a revised plan when issues are encountered
        
        Args:
            original_plan: The original plan that encountered issues
            issue: Description of the issue
            current_results: Current results obtained so far
            
        Returns:
            Dict with revised plan
        """
        prompt = get_replanning_prompt(
            json.dumps(original_plan, indent=2),
            issue,
            current_results
        )
        
        messages = [
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.grok.chat_completion(
                messages=messages,
                model=self.model,
                temperature=0.8  # Slightly higher for creativity in replanning
            )
            
            content = response["content"]
            new_plan = self._extract_json(content)
            
            if not new_plan:
                # Keep original plan if replanning fails
                new_plan = original_plan
            
            new_plan = self._validate_plan(new_plan)
            
            return {
                "success": True,
                "plan": new_plan,
                "reason": issue,
                "raw_response": content
            }
            
        except Exception as e:
            print(f"Replanning error: {e}")
            return {
                "success": False,
                "error": str(e),
                "plan": original_plan  # Fall back to original
            }
    
    def _extract_json(self, text: str) -> Optional[Dict]:
        """Extract JSON from text response"""
        # Try to find JSON in markdown code blocks
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            json_str = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            json_str = text[start:end].strip()
        else:
            # Try to parse the whole text
            json_str = text.strip()
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Try to find JSON object in text
            start_idx = text.find("{")
            end_idx = text.rfind("}") + 1
            
            if start_idx != -1 and end_idx > start_idx:
                try:
                    return json.loads(text[start_idx:end_idx])
                except:
                    pass
        
        return None
    
    def _validate_plan(self, plan: Dict) -> Dict:
        """Validate and ensure plan has required structure"""
        if not isinstance(plan, dict):
            plan = {}
        
        # Ensure required fields exist
        if "sub_tasks" not in plan:
            plan["sub_tasks"] = []
        
        if "reasoning" not in plan:
            plan["reasoning"] = "Plan created"
        
        if "expected_challenges" not in plan:
            plan["expected_challenges"] = []
        
        if "success_criteria" not in plan:
            plan["success_criteria"] = "Query answered with supporting evidence"
        
        # Validate sub-tasks
        for i, task in enumerate(plan["sub_tasks"]):
            if "id" not in task:
                task["id"] = i + 1
            if "tool" not in task:
                task["tool"] = "hybrid_retrieval"
            if "parameters" not in task:
                task["parameters"] = {}
            if "dependencies" not in task:
                task["dependencies"] = []
            if "priority" not in task:
                task["priority"] = "medium"
        
        return plan
    
    def _create_fallback_plan(self, query: str) -> Dict:
        """Create a simple fallback plan"""
        return {
            "reasoning": f"Simple search plan for: {query}",
            "sub_tasks": [
                {
                    "id": 1,
                    "description": "Search relevant data sources",
                    "tool": "hybrid_retrieval",
                    "parameters": {"query": query},
                    "dependencies": [],
                    "priority": "high"
                },
                {
                    "id": 2,
                    "description": "Analyze and synthesize results",
                    "tool": "analysis",
                    "parameters": {"query": query},
                    "dependencies": [1],
                    "priority": "high"
                }
            ],
            "expected_challenges": ["Limited data", "Ambiguous results"],
            "success_criteria": "Query answered with available data"
        }

