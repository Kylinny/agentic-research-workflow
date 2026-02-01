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
                    # Resolve parameter references to previous task results
                    resolved_task = self._resolve_task_parameters(task, results)
                    result = self.execute_task(resolved_task)
                    results[task_id] = result
                    remaining_tasks.remove(task)
                    executed_any = True
            
            if not executed_any and remaining_tasks:
                # Can't make progress - dependencies not satisfiable
                print(f"Warning: Could not satisfy dependencies for {len(remaining_tasks)} tasks")
                # Execute them anyway
                for task in remaining_tasks:
                    resolved_task = self._resolve_task_parameters(task, results)
                    result = self.execute_task(resolved_task)
                    results[task.get("id")] = result
                break
        
        # Return results in original order
        return [results.get(task.get("id"), {}) for task in tasks]
    
    def _resolve_task_parameters(self, task: Dict, previous_results: Dict) -> Dict:
        """
        Resolve parameter references to previous task results
        
        Args:
            task: Task dict that may contain parameter references
            previous_results: Dict of previous task results by task ID
            
        Returns:
            Task with resolved parameters
        """
        resolved_task = task.copy()
        parameters = task.get("parameters", {}).copy()
        tool_name = task.get("tool", "")
        dependencies = task.get("dependencies", [])
        
        # Step 1: Resolve explicit parameter references
        for param_name, param_value in list(parameters.items()):
            if isinstance(param_value, str):
                # Check for patterns like "results_from_task_1" or "task_1_results"
                if "results_from_task_" in param_value or "_task_" in param_value or "from_task" in param_value.lower():
                    # Extract task ID from the reference
                    import re
                    match = re.search(r'task[_\s]+(\d+)', param_value, re.IGNORECASE)
                    if match:
                        ref_task_id = int(match.group(1))
                        if ref_task_id in previous_results:
                            # Get the actual result data from the previous task
                            prev_result = previous_results[ref_task_id]
                            prev_tool = prev_result.get("tool", "")
                            
                            # Skip analysis tool results - they're just placeholders
                            if prev_tool == "analysis":
                                # Remove this parameter since the reference is invalid
                                parameters.pop(param_name, None)
                                continue
                            
                            if prev_result.get("success") and prev_result.get("result"):
                                # Extract the actual data based on parameter name
                                result_data = prev_result["result"]
                                try:
                                    actual_data = self._extract_relevant_data(
                                        result_data,
                                        param_name,
                                        prev_tool
                                    )
                                    if actual_data is not None:
                                        parameters[param_name] = actual_data
                                except Exception as e:
                                    # Silently continue on extraction errors
                                    pass
        
        # Step 2: Check if any parameters are still string references (failed to resolve)
        for param_name, param_value in list(parameters.items()):
            if isinstance(param_value, str) and ("task" in param_value.lower() or "from" in param_value.lower()):
                # Try to find data from any previous successful task
                for task_id, result in previous_results.items():
                    if result.get("success") and result.get("result") and result.get("tool") != "analysis":
                        extracted = self._extract_relevant_data(
                            result["result"],
                            param_name,
                            result.get("tool", "")
                        )
                        if extracted is not None:
                            parameters[param_name] = extracted
                            break
        
        # Step 3: Auto-fill missing required parameters from dependencies
        if dependencies and previous_results:
            parameters = self._auto_fill_parameters(
                tool_name,
                parameters,
                dependencies,
                previous_results
            )
        
        resolved_task["parameters"] = parameters
        return resolved_task
    
    def _auto_fill_parameters(
        self,
        tool_name: str,
        parameters: Dict,
        dependencies: List[int],
        previous_results: Dict
    ) -> Dict:
        """
        Automatically fill missing required parameters from dependency results
        
        Args:
            tool_name: Name of the tool being executed
            parameters: Current parameters dict
            dependencies: List of task IDs this task depends on
            previous_results: Dict of previous task results
            
        Returns:
            Parameters dict with auto-filled values
        """
        params = parameters.copy()
        
        # Define what each tool needs and where to get it from
        tool_requirements = {
            "sentiment_analysis": ["text", "texts", "posts"],  # Needs ONE of these
            "citation_tracker": ["paper_id"],  # Needs this
            "thread_analyzer": ["thread_id", "post_id"]  # Needs ONE of these
        }
        
        if tool_name not in tool_requirements:
            return params
        
        required_params = tool_requirements[tool_name]
        
        # Check if any required parameter is already provided
        has_required = any(param in params for param in required_params)
        if has_required:
            return params  # Already has what it needs
        
        # Try to extract required data from dependency results
        for dep_task_id in dependencies:
            if dep_task_id not in previous_results:
                continue
            
            dep_result = previous_results[dep_task_id]
            if not dep_result.get("success") or not dep_result.get("result"):
                continue
            
            dep_tool = dep_result.get("tool", "")
            
            # Skip analysis tool results - they're just placeholders
            if dep_tool == "analysis":
                continue
            
            dep_data = dep_result.get("result")
            
            # Try to extract each required parameter
            for param_name in required_params:
                if param_name not in params:  # Only fill if not already present
                    extracted = self._extract_relevant_data(dep_data, param_name, dep_tool)
                    if extracted is not None:
                        params[param_name] = extracted
                        break  # Found what we need for this tool
            
            # Check if we now have what we need
            has_required = any(param in params for param in required_params)
            if has_required:
                break
        
        return params
    
    def _extract_relevant_data(self, result_data: Any, param_name: str, source_tool: str) -> Any:
        """
        Extract relevant data from previous task results based on what's needed
        
        Args:
            result_data: The result data from a previous task
            param_name: The parameter name that needs data (e.g., 'posts', 'texts', 'paper_id')
            source_tool: The tool that produced the result
            
        Returns:
            Extracted data in the format needed by the target parameter
        """
        # Handle different parameter types
        if param_name in ["posts", "post", "post_data"]:
            # Need posts data - extract from x_search or hybrid_retrieval results
            # These tools return a direct list, not wrapped in a dict
            if isinstance(result_data, list):
                # Filter to ensure we have dicts
                valid_posts = [item for item in result_data if isinstance(item, dict)]
                return valid_posts if valid_posts else None
            elif isinstance(result_data, dict):
                # Check for multi-hop search results from hybrid_retrieval
                if "results_by_hop" in result_data:
                    # Multi-hop format: extract all results from all hops
                    all_results = []
                    for hop_data in result_data["results_by_hop"]:
                        if isinstance(hop_data, dict) and "results" in hop_data:
                            hop_results = hop_data["results"]
                            if isinstance(hop_results, list):
                                all_results.extend([r for r in hop_results if isinstance(r, dict)])
                    return all_results if all_results else None
                # Check if wrapped in dict structure
                elif "posts" in result_data:
                    posts = result_data["posts"]
                    if isinstance(posts, list):
                        return [p for p in posts if isinstance(p, dict)]
                elif "results" in result_data:
                    results = result_data["results"]
                    if isinstance(results, list):
                        return [r for r in results if isinstance(r, dict)]
                # Could be a single post object
                elif "content" in result_data or "text" in result_data:
                    return [result_data]  # Wrap single post in list
            
            # If we reach here, couldn't extract posts from the data
            return None
        
        elif param_name in ["texts", "text_list"]:
            # Need list of texts - extract text content from posts or papers
            if isinstance(result_data, list):
                # List of posts/papers - direct from x_search or hybrid_retrieval
                texts = [
                    item.get("text", item.get("content", item.get("abstract", "")))
                    for item in result_data
                    if isinstance(item, dict)
                ]
                return [t for t in texts if t]  # Filter out empty strings
            elif isinstance(result_data, dict):
                # Check for multi-hop search results
                if "results_by_hop" in result_data:
                    all_texts = []
                    for hop_data in result_data["results_by_hop"]:
                        if isinstance(hop_data, dict) and "results" in hop_data:
                            hop_results = hop_data["results"]
                            if isinstance(hop_results, list):
                                texts = [
                                    item.get("text", item.get("content", item.get("abstract", "")))
                                    for item in hop_results
                                    if isinstance(item, dict)
                                ]
                                all_texts.extend([t for t in texts if t])
                    return all_texts if all_texts else None
                elif "posts" in result_data:
                    texts = [post.get("text", post.get("content", "")) for post in result_data["posts"]]
                    return [t for t in texts if t]
                elif "results" in result_data:
                    items = result_data["results"]
                    if items and isinstance(items, list):
                        texts = [
                            item.get("text", item.get("content", item.get("abstract", "")))
                            for item in items
                        ]
                        return [t for t in texts if t]
            
            # If we reach here, couldn't extract texts from the data
            return None
        
        elif param_name in ["paper_id", "paper_ids"]:
            # Need paper ID(s) - prioritize list format from paper_search
            if isinstance(result_data, list) and len(result_data) > 0:
                first_item = result_data[0]
                if isinstance(first_item, dict):
                    return first_item.get("paper_id", first_item.get("id"))
            elif isinstance(result_data, dict):
                # Check for multi-hop results
                if "results_by_hop" in result_data:
                    for hop_data in result_data["results_by_hop"]:
                        if isinstance(hop_data, dict) and "results" in hop_data:
                            hop_results = hop_data["results"]
                            if hop_results and isinstance(hop_results, list) and len(hop_results) > 0:
                                first_result = hop_results[0]
                                if isinstance(first_result, dict):
                                    pid = first_result.get("paper_id", first_result.get("id"))
                                    if pid:
                                        return pid
                elif "paper_id" in result_data:
                    return result_data["paper_id"]
                elif "results" in result_data:
                    results = result_data["results"]
                    if results and isinstance(results, list) and len(results) > 0:
                        first_result = results[0]
                        if isinstance(first_result, dict):
                            return first_result.get("paper_id", first_result.get("id"))
            
            # If we reach here, couldn't extract paper_id from the data
            return None
        
        elif param_name in ["thread_id", "post_id"]:
            # Need thread or post ID - prioritize list format from x_search
            if isinstance(result_data, list) and len(result_data) > 0:
                first_item = result_data[0]
                if isinstance(first_item, dict):
                    return first_item.get("post_id", first_item.get("id", first_item.get("thread_id")))
            elif isinstance(result_data, dict):
                # Check for multi-hop results
                if "results_by_hop" in result_data:
                    for hop_data in result_data["results_by_hop"]:
                        if isinstance(hop_data, dict) and "results" in hop_data:
                            hop_results = hop_data["results"]
                            if hop_results and isinstance(hop_results, list) and len(hop_results) > 0:
                                first_result = hop_results[0]
                                if isinstance(first_result, dict):
                                    post_id = first_result.get("post_id", first_result.get("id", first_result.get("thread_id")))
                                    if post_id:
                                        return post_id
                elif "thread_id" in result_data:
                    return result_data["thread_id"]
                elif "post_id" in result_data:
                    return result_data["post_id"]
                elif "posts" in result_data:
                    posts = result_data["posts"]
                    if posts and isinstance(posts, list) and len(posts) > 0:
                        first_post = posts[0]
                        if isinstance(first_post, dict):
                            return first_post.get("post_id", first_post.get("id"))
                elif "results" in result_data:
                    results = result_data["results"]
                    if results and isinstance(results, list) and len(results) > 0:
                        first_result = results[0]
                        if isinstance(first_result, dict):
                            return first_result.get("post_id", first_result.get("id"))
            
            # If we reach here, couldn't extract thread_id/post_id from the data
            return None
        
        # Unknown parameter type - return None to trigger auto-fill
        return None
    
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
            text_val = params["text"]
            # Ensure it's a string
            if isinstance(text_val, str):
                return tool.analyze(text_val)
            else:
                raise ValueError(f"'text' parameter must be a string, got {type(text_val).__name__}")
        elif "texts" in params:
            texts_val = params["texts"]
            # Ensure it's a list of strings
            if isinstance(texts_val, list):
                # Filter out non-strings and empty strings
                valid_texts = [t for t in texts_val if isinstance(t, str) and t.strip()]
                if valid_texts:
                    return tool.analyze_batch(valid_texts)
                else:
                    raise ValueError("'texts' parameter contains no valid text strings")
            else:
                raise ValueError(f"'texts' parameter must be a list, got {type(texts_val).__name__}")
        elif "posts" in params:
            posts_val = params["posts"]
            
            # Ensure it's a list of dicts
            if isinstance(posts_val, list):
                # Filter out non-dict items
                valid_posts = [p for p in posts_val if isinstance(p, dict)]
                if not valid_posts:
                    raise ValueError(f"'posts' parameter contains no valid post objects (got {len(posts_val)} items, 0 are dicts)")
                
                if params.get("type") == "thread":
                    return tool.analyze_thread(valid_posts)
                else:
                    return tool.aggregate_sentiment(valid_posts)
            else:
                raise ValueError(f"'posts' parameter must be a list of post objects, got {type(posts_val).__name__}")
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

