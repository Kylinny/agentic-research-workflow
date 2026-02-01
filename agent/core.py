"""
Core Research Agent with iterative loop
"""
import os
from typing import Dict, Optional
from colorama import Fore, Style, init
from grok import GrokClient, GrokModel
from .planner import AgentPlanner
from .executor import ToolExecutor
from .analyzer import ResultAnalyzer
from .context_manager import ContextManager

init(autoreset=True)

class ResearchAgent:
    """
    Autonomous research agent with iterative loop:
    plan → decompose → execute tools → analyze → refine → summarize
    """
    
    def __init__(
        self,
        grok_client: Optional[GrokClient] = None,
        model: GrokModel = GrokModel.GROK_4_LATEST,
        max_iterations: int = 10,
        data_dir: str = "data"
    ):
        """
        Initialize the research agent
        
        Args:
            grok_client: Grok API client (creates default if None)
            model: Grok model variant to use
            max_iterations: Maximum number of agent iterations
            data_dir: Directory containing data files
        """
        self.grok = grok_client or GrokClient()
        self.model = model
        self.max_iterations = max_iterations
        self.data_dir = data_dir
        
        # Initialize components
        self.planner = AgentPlanner(self.grok, model)
        self.executor = ToolExecutor(data_dir)
        self.analyzer = ResultAnalyzer(self.grok, model)
        self.context = ContextManager()
        
        print(f"{Fore.GREEN}✓ Research Agent initialized with {model.display_name}")
    
    def research(self, query: str, verbose: bool = True) -> Dict:
        """
        Execute full research workflow for a query
        
        Args:
            query: Research query
            verbose: Whether to print progress
            
        Returns:
            Dict with final results and metadata
        """
        if verbose:
            print(f"\n{Fore.CYAN}{'='*60}")
            print(f"Research Query: {query}")
            print(f"{'='*60}{Style.RESET_ALL}\n")
        
        iteration = 0
        current_plan = None
        all_results = []
        
        while iteration < self.max_iterations:
            iteration += 1
            
            if verbose:
                print(f"{Fore.YELLOW}[Iteration {iteration}/{self.max_iterations}]{Style.RESET_ALL}")
            
            # Step 1: Planning (or replanning)
            if current_plan is None:
                if verbose:
                    print(f"{Fore.BLUE}→ Creating initial plan...{Style.RESET_ALL}")
                
                context = self.context.get_context_summary()
                plan_result = self.planner.create_plan(query, context)
                
                if not plan_result["success"]:
                    if verbose:
                        print(f"{Fore.RED}✗ Planning failed: {plan_result.get('error')}{Style.RESET_ALL}")
                    break
                
                current_plan = plan_result["plan"]
                self.context.set_plan(current_plan)
                
                if verbose:
                    print(f"{Fore.GREEN}✓ Plan created with {len(current_plan['sub_tasks'])} tasks{Style.RESET_ALL}")
            
            # Step 2: Execute tasks
            if verbose:
                print(f"{Fore.BLUE}→ Executing tasks...{Style.RESET_ALL}")
            
            tasks = current_plan.get("sub_tasks", [])
            execution_results = self.executor.execute_tasks(tasks)
            all_results.extend(execution_results)
            
            # Record results in context
            for task, result in zip(tasks, execution_results):
                self.context.add_tool_result(
                    task.get("tool"),
                    task.get("parameters", {}),
                    result
                )
            
            success_count = sum(1 for r in execution_results if r.get("success"))
            if verbose:
                print(f"{Fore.GREEN}✓ Executed {len(execution_results)} tasks ({success_count} successful){Style.RESET_ALL}")
            
            # Step 3: Analyze results
            if verbose:
                print(f"{Fore.BLUE}→ Analyzing results...{Style.RESET_ALL}")
            
            analysis_result = self.analyzer.analyze_results(
                execution_results,
                query,
                iteration,
                len(current_plan.get("sub_tasks", []))
            )
            
            if not analysis_result["success"]:
                if verbose:
                    print(f"{Fore.RED}✗ Analysis failed: {analysis_result.get('error')}{Style.RESET_ALL}")
                break
            
            analysis = analysis_result["analysis"]
            self.context.add_analysis(analysis)
            
            if verbose:
                print(f"{Fore.GREEN}✓ Analysis complete (quality: {analysis['quality_score']:.1f}/10){Style.RESET_ALL}")
            
            # Step 4: Check if replanning is needed
            if analysis.get("needs_replanning", False):
                if verbose:
                    print(f"{Fore.YELLOW}⚠ Replanning needed: {analysis['replan_reason']}{Style.RESET_ALL}")
                
                replan_result = self.planner.replan(
                    current_plan,
                    analysis["replan_reason"],
                    analysis.get("synthesis", "")
                )
                
                if replan_result["success"]:
                    current_plan = replan_result["plan"]
                    self.context.add_replan(
                        analysis["replan_reason"],
                        current_plan
                    )
                    if verbose:
                        print(f"{Fore.GREEN}✓ New plan created{Style.RESET_ALL}")
                else:
                    if verbose:
                        print(f"{Fore.RED}✗ Replanning failed, continuing...{Style.RESET_ALL}")
            
            # Step 5: Check if we have sufficient results
            elif analysis["quality_score"] >= 7.0 and analysis["completeness"] >= 7.0:
                if verbose:
                    print(f"{Fore.GREEN}✓ Sufficient results obtained{Style.RESET_ALL}")
                break
            
            # Check if we should continue
            if success_count == 0 and iteration > 1:
                if verbose:
                    print(f"{Fore.RED}✗ No successful tasks, stopping{Style.RESET_ALL}")
                break
        
        # Step 6: Final synthesis
        if verbose:
            print(f"\n{Fore.BLUE}→ Synthesizing final results...{Style.RESET_ALL}")
        
        execution_trace = self.context.get_context_summary()
        synthesis_result = self.analyzer.synthesize_final_results(
            all_results,
            query,
            execution_trace
        )
        
        if verbose:
            if synthesis_result["success"]:
                print(f"{Fore.GREEN}✓ Synthesis complete{Style.RESET_ALL}\n")
            else:
                print(f"{Fore.RED}✗ Synthesis failed{Style.RESET_ALL}\n")
        
        # Evaluate answer quality
        if synthesis_result["success"]:
            quality_metrics = self.analyzer.evaluate_answer_quality(
                synthesis_result["synthesis"],
                query
            )
        else:
            quality_metrics = {}
        
        # Prepare final output
        final_result = {
            "query": query,
            "success": synthesis_result["success"],
            "answer": synthesis_result.get("synthesis", ""),
            "model_used": self.model.value,
            "iterations": iteration,
            "total_tasks": len(all_results),
            "successful_tasks": sum(1 for r in all_results if r.get("success")),
            "replans": self.context.get_statistics()["replans"],
            "quality_metrics": quality_metrics,
            "execution_trace": self.context.export_trace(),
            "token_usage": synthesis_result.get("token_usage", {})
        }
        
        return final_result
    
    def reset(self):
        """Reset agent state for a new query"""
        self.context.clear_context()
    
    def get_statistics(self) -> Dict:
        """Get statistics about agent execution"""
        return self.context.get_statistics()

