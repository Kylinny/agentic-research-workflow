"""
Context manager for maintaining conversation history and state
"""
from typing import List, Dict, Optional
import json

class ContextManager:
    """Manages context and memory across agent iterations"""
    
    def __init__(self, max_context_size: int = 8000):
        self.max_context_size = max_context_size
        self.history = []
        self.current_plan = None
        self.execution_trace = []
        self.key_insights = []
        
    def add_step(self, step_type: str, content: Dict):
        """Add a step to the execution trace"""
        self.execution_trace.append({
            "type": step_type,
            "content": content,
            "step_number": len(self.execution_trace) + 1
        })
        
        self.history.append({
            "type": step_type,
            "content": content
        })
    
    def set_plan(self, plan: Dict):
        """Set the current execution plan"""
        self.current_plan = plan
        self.add_step("plan", plan)
    
    def add_tool_result(self, tool_name: str, parameters: Dict, result: any):
        """Add a tool execution result"""
        self.add_step("tool_execution", {
            "tool": tool_name,
            "parameters": parameters,
            "result": result
        })
    
    def add_analysis(self, analysis: Dict):
        """Add an analysis result"""
        self.add_step("analysis", analysis)
        
        # Extract insights
        if "synthesis" in analysis:
            self.key_insights.append(analysis["synthesis"])
    
    def add_replan(self, reason: str, new_plan: Dict):
        """Add a replanning event"""
        self.add_step("replan", {
            "reason": reason,
            "new_plan": new_plan
        })
        self.current_plan = new_plan
    
    def get_context_summary(self, max_tokens: Optional[int] = None) -> str:
        """
        Get a summary of the current context
        
        Args:
            max_tokens: Optional token limit for summary
            
        Returns:
            String summary of context
        """
        summary_parts = []
        
        # Current plan
        if self.current_plan:
            summary_parts.append("## Current Plan")
            summary_parts.append(json.dumps(self.current_plan, indent=2))
        
        # Key insights
        if self.key_insights:
            summary_parts.append("\n## Key Insights")
            for i, insight in enumerate(self.key_insights, 1):
                summary_parts.append(f"{i}. {insight}")
        
        # Recent execution trace
        summary_parts.append("\n## Recent Steps")
        recent_steps = self.execution_trace[-5:]  # Last 5 steps
        for step in recent_steps:
            step_summary = self._summarize_step(step)
            summary_parts.append(step_summary)
        
        full_summary = "\n".join(summary_parts)
        
        # Truncate if necessary
        if max_tokens and len(full_summary.split()) > max_tokens:
            words = full_summary.split()
            truncated = " ".join(words[:max_tokens])
            return truncated + "\n\n[Context truncated]"
        
        return full_summary
    
    def get_relevant_context(self, query: str) -> str:
        """
        Get context relevant to a specific query
        
        Args:
            query: The query to find relevant context for
            
        Returns:
            Relevant context string
        """
        # Simple relevance: check if query terms appear in step content
        query_terms = set(query.lower().split())
        relevant_steps = []
        
        for step in self.execution_trace:
            step_text = json.dumps(step).lower()
            step_terms = set(step_text.split())
            
            # Calculate overlap
            overlap = len(query_terms & step_terms)
            if overlap > 0:
                relevant_steps.append((step, overlap))
        
        # Sort by relevance
        relevant_steps.sort(key=lambda x: x[1], reverse=True)
        
        # Format top relevant steps
        context_parts = []
        for step, _ in relevant_steps[:5]:
            context_parts.append(self._summarize_step(step))
        
        return "\n".join(context_parts)
    
    def _summarize_step(self, step: Dict) -> str:
        """Summarize a single step"""
        step_type = step["type"]
        step_num = step.get("step_number", "?")
        
        if step_type == "plan":
            num_tasks = len(step["content"].get("sub_tasks", []))
            return f"Step {step_num}: Created plan with {num_tasks} sub-tasks"
        
        elif step_type == "tool_execution":
            tool = step["content"]["tool"]
            return f"Step {step_num}: Executed {tool}"
        
        elif step_type == "analysis":
            quality = step["content"].get("quality_score", "?")
            return f"Step {step_num}: Analysis (quality: {quality}/10)"
        
        elif step_type == "replan":
            reason = step["content"]["reason"]
            return f"Step {step_num}: Replanned due to: {reason}"
        
        else:
            return f"Step {step_num}: {step_type}"
    
    def clear_context(self):
        """Clear all context"""
        self.history = []
        self.current_plan = None
        self.execution_trace = []
        self.key_insights = []
    
    def get_statistics(self) -> Dict:
        """Get statistics about the context"""
        tool_executions = sum(1 for s in self.execution_trace if s["type"] == "tool_execution")
        replans = sum(1 for s in self.execution_trace if s["type"] == "replan")
        
        return {
            "total_steps": len(self.execution_trace),
            "tool_executions": tool_executions,
            "replans": replans,
            "insights_collected": len(self.key_insights),
            "has_plan": self.current_plan is not None
        }
    
    def export_trace(self) -> List[Dict]:
        """Export full execution trace"""
        return self.execution_trace.copy()

