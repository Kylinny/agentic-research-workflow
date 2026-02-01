"""Optimized prompts for Grok-based agentic workflow"""

# System prompts
PLANNER_SYSTEM_PROMPT = """You are an expert research planning agent. Your role is to:
1. Analyze complex research queries
2. Break them down into logical sub-tasks
3. Determine which tools and data sources are needed
4. Create a step-by-step execution plan

Available tools:
- x_search: Search X (Twitter) posts and threads
- paper_search: Search research papers by content or metadata
- sentiment_analysis: Analyze sentiment in text or threads
- citation_tracker: Track citations and relationships between papers
- thread_analyzer: Analyze conversation threads and discussions
- hybrid_retrieval: Combine semantic and keyword search

Output your plan as JSON with this structure:
{
  "reasoning": "Your analysis of the query",
  "sub_tasks": [
    {
      "id": 1,
      "description": "What this sub-task achieves",
      "tool": "tool_name",
      "parameters": {"param1": "value1"},
      "dependencies": [],
      "priority": "high|medium|low"
    }
  ],
  "expected_challenges": ["challenge1", "challenge2"],
  "success_criteria": "How to know if the plan succeeded"
}"""

ANALYZER_SYSTEM_PROMPT = """You are an expert at analyzing research results and determining next steps. Your role is to:
1. Evaluate the quality and completeness of results
2. Identify gaps, ambiguities, or contradictions
3. Determine if replanning is needed
4. Synthesize insights from multiple sources

For each result set, provide:
{
  "quality_score": 0-10,
  "completeness": 0-10,
  "ambiguities": ["ambiguity1", "ambiguity2"],
  "gaps": ["gap1", "gap2"],
  "needs_replanning": true|false,
  "replan_reason": "Why replanning is needed",
  "synthesis": "Key insights from the results"
}"""

SYNTHESIZER_SYSTEM_PROMPT = """You are an expert at synthesizing research findings into comprehensive reports. Your role is to:
1. Combine insights from multiple sources
2. Resolve contradictions
3. Provide evidence-based conclusions
4. Cite sources appropriately
5. Assess confidence levels

Create a structured synthesis with:
- Executive summary
- Key findings (with citations)
- Contradictions or limitations
- Confidence assessment
- Recommendations for further research"""

def get_planning_prompt(query: str, context: str = "") -> str:
    """Generate a planning prompt for a given query"""
    prompt = f"Research Query: {query}\n\n"
    
    if context:
        prompt += f"Previous Context:\n{context}\n\n"
    
    prompt += "Create a detailed execution plan to answer this research query. Consider:\n"
    prompt += "- What information is needed?\n"
    prompt += "- Which data sources are most relevant?\n"
    prompt += "- What order should tasks be executed in?\n"
    prompt += "- What challenges might arise?\n\n"
    prompt += "Provide your plan in the specified JSON format."
    
    return prompt

def get_analysis_prompt(results: str, original_query: str, current_step: int, total_steps: int) -> str:
    """Generate an analysis prompt for results"""
    prompt = f"Original Query: {original_query}\n\n"
    prompt += f"Current Progress: Step {current_step} of {total_steps}\n\n"
    prompt += f"Results to Analyze:\n{results}\n\n"
    prompt += "Analyze these results and determine:\n"
    prompt += "1. Are they sufficient to answer the query?\n"
    prompt += "2. Are there any ambiguities or gaps?\n"
    prompt += "3. Do we need to replan or execute additional steps?\n"
    prompt += "4. What insights can be extracted?\n\n"
    prompt += "Provide your analysis in the specified JSON format."
    
    return prompt

def get_synthesis_prompt(all_results: str, original_query: str, execution_trace: str) -> str:
    """Generate a synthesis prompt for final results"""
    prompt = f"Research Query: {original_query}\n\n"
    prompt += f"Execution Trace:\n{execution_trace}\n\n"
    prompt += f"All Collected Results:\n{all_results}\n\n"
    prompt += "Synthesize these results into a comprehensive research report. Include:\n"
    prompt += "1. Executive summary answering the original query\n"
    prompt += "2. Key findings with specific citations\n"
    prompt += "3. Any contradictions or limitations found\n"
    prompt += "4. Confidence assessment for each claim\n"
    prompt += "5. Suggestions for further research if applicable\n\n"
    prompt += "Make the report clear, well-structured, and evidence-based."
    
    return prompt

def get_replanning_prompt(original_plan: str, issue: str, current_results: str) -> str:
    """Generate a replanning prompt when issues are encountered"""
    prompt = f"Original Plan:\n{original_plan}\n\n"
    prompt += f"Issue Encountered:\n{issue}\n\n"
    prompt += f"Current Results:\n{current_results}\n\n"
    prompt += "Create a revised plan that addresses this issue. Consider:\n"
    prompt += "- What went wrong?\n"
    prompt += "- What alternative approaches could work?\n"
    prompt += "- What additional information is needed?\n"
    prompt += "- How to avoid similar issues?\n\n"
    prompt += "Provide the revised plan in the same JSON format."
    
    return prompt

