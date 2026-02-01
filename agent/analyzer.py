"""
Result analyzer for evaluating results and determining next steps
"""
import json
from typing import Dict, List
from grok import GrokClient, GrokModel
from grok.prompts import ANALYZER_SYSTEM_PROMPT, SYNTHESIZER_SYSTEM_PROMPT, get_analysis_prompt, get_synthesis_prompt

class ResultAnalyzer:
    """Analyzes results and determines if replanning is needed"""
    
    def __init__(self, grok_client: GrokClient, model: GrokModel = GrokModel.GROK_4_LATEST):
        self.grok = grok_client
        self.model = model
    
    def analyze_results(
        self,
        results: List[Dict],
        original_query: str,
        current_step: int,
        total_steps: int
    ) -> Dict:
        """
        Analyze execution results and determine next steps
        
        Args:
            results: List of task execution results
            original_query: The original research query
            current_step: Current step number
            total_steps: Total planned steps
            
        Returns:
            Dict with analysis and recommendations
        """
        # Format results for analysis
        results_text = self._format_results(results)
        
        prompt = get_analysis_prompt(
            results_text,
            original_query,
            current_step,
            total_steps
        )
        
        messages = [
            {"role": "system", "content": ANALYZER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.grok.chat_completion(
                messages=messages,
                model=self.model,
                temperature=0.6
            )
            
            content = response["content"]
            analysis = self._extract_json(content)
            
            if not analysis:
                # Create basic analysis if parsing fails
                analysis = self._create_basic_analysis(results)
            
            # Ensure required fields
            analysis = self._validate_analysis(analysis)
            
            return {
                "success": True,
                "analysis": analysis,
                "raw_response": content
            }
            
        except Exception as e:
            print(f"Analysis error: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis": self._create_basic_analysis(results)
            }
    
    def synthesize_final_results(
        self,
        all_results: List[Dict],
        original_query: str,
        execution_trace: str
    ) -> Dict:
        """
        Synthesize all results into a final comprehensive report
        
        Args:
            all_results: All execution results
            original_query: Original research query
            execution_trace: Summary of execution steps
            
        Returns:
            Dict with final synthesis
        """
        results_text = self._format_results(all_results)
        
        prompt = get_synthesis_prompt(
            results_text,
            original_query,
            execution_trace
        )
        
        messages = [
            {"role": "system", "content": SYNTHESIZER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.grok.chat_completion(
                messages=messages,
                model=self.model,
                temperature=0.7,
                max_tokens=4096
            )
            
            synthesis = response["content"]
            
            return {
                "success": True,
                "synthesis": synthesis,
                "model_used": response["model"],
                "token_usage": response["usage"]
            }
            
        except Exception as e:
            print(f"Synthesis error: {e}")
            return {
                "success": False,
                "error": str(e),
                "synthesis": "Failed to synthesize results. See error details."
            }
    
    def evaluate_answer_quality(self, synthesis: str, original_query: str) -> Dict:
        """
        Evaluate the quality of the final answer
        
        Args:
            synthesis: The synthesized answer
            original_query: Original query
            
        Returns:
            Dict with quality metrics
        """
        # Simple heuristic-based quality evaluation
        metrics = {
            "completeness": 0.0,
            "coherence": 0.0,
            "evidence_support": 0.0,
            "overall_score": 0.0
        }
        
        # Completeness: Does it address the query?
        query_terms = set(original_query.lower().split())
        synthesis_terms = set(synthesis.lower().split())
        term_coverage = len(query_terms & synthesis_terms) / max(len(query_terms), 1)
        metrics["completeness"] = min(term_coverage * 1.5, 1.0)
        
        # Coherence: Length and structure
        word_count = len(synthesis.split())
        if word_count >= 100:
            metrics["coherence"] = 0.8
        elif word_count >= 50:
            metrics["coherence"] = 0.6
        else:
            metrics["coherence"] = 0.4
        
        # Evidence support: Check for citations or data references
        evidence_indicators = [
            "according to", "research shows", "data indicates",
            "paper", "study", "post", "thread", "author"
        ]
        evidence_count = sum(
            1 for indicator in evidence_indicators
            if indicator in synthesis.lower()
        )
        metrics["evidence_support"] = min(evidence_count / 3.0, 1.0)
        
        # Overall score
        metrics["overall_score"] = (
            metrics["completeness"] * 0.4 +
            metrics["coherence"] * 0.3 +
            metrics["evidence_support"] * 0.3
        )
        
        return metrics
    
    def _format_results(self, results: List[Dict]) -> str:
        """Format results for prompting"""
        formatted_parts = []
        
        for i, result in enumerate(results, 1):
            if not result.get("success", False):
                formatted_parts.append(
                    f"Task {i} ({result.get('tool', 'unknown')}): FAILED\n"
                    f"Error: {result.get('error', 'Unknown error')}"
                )
                continue
            
            task_result = result.get("result", {})
            
            # Truncate large results
            result_str = json.dumps(task_result, indent=2)
            if len(result_str) > 2000:
                result_str = result_str[:2000] + "\n... [truncated]"
            
            formatted_parts.append(
                f"Task {i} ({result.get('tool', 'unknown')}):\n{result_str}"
            )
        
        return "\n\n".join(formatted_parts)
    
    def _extract_json(self, text: str) -> Dict:
        """Extract JSON from text"""
        # Try markdown code blocks
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            json_str = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            json_str = text[start:end].strip()
        else:
            json_str = text.strip()
        
        try:
            return json.loads(json_str)
        except:
            # Try to find JSON object
            start_idx = text.find("{")
            end_idx = text.rfind("}") + 1
            
            if start_idx != -1 and end_idx > start_idx:
                try:
                    return json.loads(text[start_idx:end_idx])
                except:
                    pass
        
        return None
    
    def _create_basic_analysis(self, results: List[Dict]) -> Dict:
        """Create basic analysis when Grok analysis fails"""
        success_count = sum(1 for r in results if r.get("success", False))
        
        return {
            "quality_score": (success_count / max(len(results), 1)) * 10,
            "completeness": 7.0 if success_count > 0 else 3.0,
            "ambiguities": [],
            "gaps": ["Could not perform detailed analysis"],
            "needs_replanning": success_count == 0,
            "replan_reason": "All tasks failed" if success_count == 0 else "",
            "synthesis": f"Executed {len(results)} tasks, {success_count} successful."
        }
    
    def _validate_analysis(self, analysis: Dict) -> Dict:
        """Ensure analysis has required fields"""
        defaults = {
            "quality_score": 5.0,
            "completeness": 5.0,
            "ambiguities": [],
            "gaps": [],
            "needs_replanning": False,
            "replan_reason": "",
            "synthesis": ""
        }
        
        for key, default_value in defaults.items():
            if key not in analysis:
                analysis[key] = default_value
        
        return analysis

