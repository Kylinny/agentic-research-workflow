"""
Tool executor for running planned tasks
"""
from typing import Dict, Any, List
from tools import (
    XSearchTool,
    PaperSearchTool,
    SentimentAnalysisTool,
    CitationTrackerTool,
    HybridRetrievalTool
)

class ToolExecutor:
    """Executes tools based on plan tasks"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.tools = {}
        self._initialize_tools()
    
    def _initialize_tools(self):
        """Initialize all available tools"""
        try:
            self.tools["x_search"] = XSearchTool(
                data_path=f"{self.data_dir}/x_posts.json"
            )
            self.tools["paper_search"] = PaperSearchTool(
                data_path=f"{self.data_dir}/research_papers.json"
            )
            self.tools["sentiment_analysis"] = SentimentAnalysisTool()
            self.tools["citation_tracker"] = CitationTrackerTool(
                data_path=f"{self.data_dir}/research_papers.json"
            )
            self.tools["hybrid_retrieval"] = HybridRetrievalTool(
                data_dir=self.data_dir
            )
            print("✓ All tools initialized successfully")
        except Exception as e:
            print(f"Warning: Some tools failed to initialize: {e}")
    
    def execute_task(self, task: Dict) -> Dict:
        """
        Execute a single task
        
        Args:
            task: Task dict with tool, parameters, etc.
            
        Returns:
            Dict with execution results
        """
        tool_name = task.get("tool", "")
        parameters = task.get("parameters", {})
        task_id = task.get("id", "unknown")
        
        print(f"Executing task {task_id}: {tool_name}")
        
        try:
            result = self._call_tool(tool_name, parameters)
            
            return {
                "success": True,
                "task_id": task_id,
                "tool": tool_name,
                "result": result,
                "error": None
            }
            
        except Exception as e:
            print(f"Task {task_id} failed: {e}")
            return {
                "success": False,
                "task_id": task_id,
                "tool": tool_name,
                "result": None,
                "error": str(e)
            }
    
    def execute_tasks(self, tasks: List[Dict], respect_dependencies: bool = True) -> List[Dict]:
        """
        Execute multiple tasks respecting dependencies
        
        Args:
            tasks: List of task dicts
            respect_dependencies: Whether to respect task dependencies
            
        Returns:
            List of execution results
        """
        if not respect_dependencies:
            return [self.execute_task(task) for task in tasks]
        
        # Execute tasks in dependency order
        results = {}
        remaining_tasks = tasks.copy()
        
        max_iterations = len(tasks) * 2  # Prevent infinite loops
        iteration = 0
        
        while remaining_tasks and iteration < max_iterations:
            iteration += 1
            executed_any = False
            
            for task in remaining_tasks[:]:
                task_id = task.get("id")
                dependencies = task.get("dependencies", [])
                
                # Check if all dependencies are satisfied
                deps_satisfied = all(dep in results for dep in dependencies)
                
                if deps_satisfied:
                    result = self.execute_task(task)
                    results[task_id] = result
                    remaining_tasks.remove(task)
                    executed_any = True
            
            if not executed_any and remaining_tasks:
                # Can't make progress - dependencies not satisfiable
                print(f"Warning: Could not satisfy dependencies for {len(remaining_tasks)} tasks")
                # Execute them anyway
                for task in remaining_tasks:
                    result = self.execute_task(task)
                    results[task.get("id")] = result
                break
        
        # Return results in original order
        return [results.get(task.get("id"), {}) for task in tasks]
    
    def _call_tool(self, tool_name: str, parameters: Dict) -> Any:
        """
        Call a specific tool with parameters
        
        Args:
            tool_name: Name of the tool
            parameters: Tool parameters
            
        Returns:
            Tool execution result
        """
        # Map tool names to methods
        tool_map = {
            "x_search": self._execute_x_search,
            "paper_search": self._execute_paper_search,
            "sentiment_analysis": self._execute_sentiment_analysis,
            "citation_tracker": self._execute_citation_tracker,
            "hybrid_retrieval": self._execute_hybrid_retrieval,
            "thread_analyzer": self._execute_thread_analyzer,
            "analysis": self._execute_analysis
        }
        
        executor = tool_map.get(tool_name)
        
        if not executor:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        return executor(parameters)
    
    def _execute_x_search(self, params: Dict) -> Any:
        """Execute X search tool"""
        tool = self.tools["x_search"]
        query = params.get("query", "")
        filters = params.get("filters", None)
        limit = params.get("limit", 20)
        
        return tool.search(query, filters, limit)
    
    def _execute_paper_search(self, params: Dict) -> Any:
        """Execute paper search tool"""
        tool = self.tools["paper_search"]
        query = params.get("query", "")
        filters = params.get("filters", None)
        limit = params.get("limit", 20)
        
        return tool.search(query, filters, limit)
    
    def _execute_sentiment_analysis(self, params: Dict) -> Any:
        """Execute sentiment analysis tool"""
        tool = self.tools["sentiment_analysis"]
        
        if "text" in params:
            return tool.analyze(params["text"])
        elif "texts" in params:
            return tool.analyze_batch(params["texts"])
        elif "posts" in params:
            if params.get("type") == "thread":
                return tool.analyze_thread(params["posts"])
            else:
                return tool.aggregate_sentiment(params["posts"])
        else:
            raise ValueError("sentiment_analysis requires 'text', 'texts', or 'posts' parameter")
    
    def _execute_citation_tracker(self, params: Dict) -> Any:
        """Execute citation tracker tool"""
        tool = self.tools["citation_tracker"]
        
        action = params.get("action", "get_citations")
        
        if action == "get_citations":
            return tool.get_citations(params["paper_id"])
        elif action == "get_cited_by":
            return tool.get_cited_by(params["paper_id"])
        elif action == "find_influential":
            return tool.find_influential_papers(
                params.get("min_citations", 10),
                params.get("limit", 20)
            )
        elif action == "citation_network":
            return tool.build_citation_graph(
                params["seed_papers"],
                params.get("max_depth", 2)
            )
        elif action == "impact_metrics":
            return tool.calculate_impact_metrics(params["paper_id"])
        else:
            raise ValueError(f"Unknown citation_tracker action: {action}")
    
    def _execute_hybrid_retrieval(self, params: Dict) -> Any:
        """Execute hybrid retrieval tool"""
        tool = self.tools["hybrid_retrieval"]
        query = params.get("query", "")
        doc_type = params.get("doc_type", "x_posts")
        top_k = params.get("top_k", 10)
        filters = params.get("filters", None)
        
        if params.get("multi_hop", False):
            return tool.multi_hop_search(
                query,
                doc_type,
                params.get("hops", 2),
                top_k
            )
        else:
            return tool.search(query, doc_type, top_k, filters=filters)
    
    def _execute_thread_analyzer(self, params: Dict) -> Any:
        """Analyze threads"""
        tool = self.tools["x_search"]
        
        if "thread_id" in params:
            return tool.get_thread(params["thread_id"])
        elif "post_id" in params:
            return tool.get_conversation(params["post_id"])
        else:
            raise ValueError("thread_analyzer requires 'thread_id' or 'post_id'")
    
    def _execute_analysis(self, params: Dict) -> Any:
        """Generic analysis placeholder"""
        # This is a meta-task that would be handled by the analyzer
        return {
            "note": "Analysis task - handled by analyzer component",
            "parameters": params
        }

