"""
Run benchmark evaluation on test queries
"""
import json
import os
import sys
import time
from datetime import datetime
from typing import List, Dict
from tqdm import tqdm

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grok import GrokModel, OfflineGrokClient
from agent import ResearchAgent

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv:
    load_dotenv()

def load_queries(query_file: str = "evaluation/queries.json") -> List[Dict]:
    """Load test queries"""
    with open(query_file, 'r') as f:
        data = json.load(f)
    return data["queries"]

def run_benchmark(
    queries: List[Dict],
    model: GrokModel = GrokModel.GROK_4_LATEST,
    max_queries: int = None,
    output_dir: str = "results/benchmark",
    offline: bool = False
):
    """
    Run benchmark on queries
    
    Args:
        queries: List of query dicts
        model: Grok model to use
        max_queries: Maximum number of queries to run (None for all)
        output_dir: Directory to save results
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize agent
    print(f"Initializing agent with {model.display_name}...")
    agent = ResearchAgent(
        grok_client=OfflineGrokClient() if offline else None,
        model=model
    )
    
    # Select queries
    if max_queries:
        queries = queries[:max_queries]
    
    print(f"Running benchmark on {len(queries)} queries...\n")
    
    results = []
    stats = {
        "total_queries": len(queries),
        "successful": 0,
        "failed": 0,
        "total_iterations": 0,
        "total_tasks": 0,
        "total_replans": 0,
        "total_time": 0,
        "model": model.value
    }
    
    for i, query_data in enumerate(tqdm(queries, desc="Evaluating")):
        query_id = query_data["id"]
        query = query_data["query"]
        
        print(f"\n[{i+1}/{len(queries)}] Query {query_id}: {query[:60]}...")
        
        start_time = time.time()
        
        try:
            result = agent.research(query, verbose=False)
            elapsed = time.time() - start_time
            
            result["query_id"] = query_id
            result["category"] = query_data.get("category", "unknown")
            result["complexity"] = query_data.get("complexity", "unknown")
            result["elapsed_time"] = elapsed
            
            results.append(result)
            
            # Update stats
            if result["success"]:
                stats["successful"] += 1
            else:
                stats["failed"] += 1
            
            stats["total_iterations"] += result["iterations"]
            stats["total_tasks"] += result["total_tasks"]
            stats["total_replans"] += result["replans"]
            stats["total_time"] += elapsed
            
            print(f"✓ Complete in {elapsed:.1f}s (Quality: {result['quality_metrics'].get('overall_score', 0):.2f})")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            results.append({
                "query_id": query_id,
                "query": query,
                "success": False,
                "error": str(e),
                "elapsed_time": time.time() - start_time
            })
            stats["failed"] += 1
        
        # Reset agent for next query
        agent.reset()
        
        # Small delay to avoid rate limits
        time.sleep(1)
    
    # Calculate averages
    stats["avg_iterations"] = stats["total_iterations"] / len(queries)
    stats["avg_tasks"] = stats["total_tasks"] / len(queries)
    stats["avg_replans"] = stats["total_replans"] / len(queries)
    stats["avg_time"] = stats["total_time"] / len(queries)
    stats["completion_rate"] = stats["successful"] / len(queries)
    
    # Calculate quality metrics
    successful_results = [r for r in results if r.get("success", False)]
    if successful_results:
        quality_scores = [r["quality_metrics"]["overall_score"] 
                         for r in successful_results 
                         if "quality_metrics" in r]
        if quality_scores:
            stats["avg_quality_score"] = sum(quality_scores) / len(quality_scores)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join(output_dir, f"benchmark_{model.value}_{timestamp}.json")
    
    output = {
        "timestamp": timestamp,
        "model": model.value,
        "statistics": stats,
        "results": results
    }
    
    with open(results_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n{'='*70}")
    print("BENCHMARK RESULTS")
    print('='*70)
    print(f"Model: {model.display_name}")
    print(f"Queries: {stats['total_queries']}")
    print(f"Successful: {stats['successful']} ({stats['completion_rate']*100:.1f}%)")
    print(f"Failed: {stats['failed']}")
    print(f"Avg Iterations: {stats['avg_iterations']:.1f}")
    print(f"Avg Tasks: {stats['avg_tasks']:.1f}")
    print(f"Avg Replans: {stats['avg_replans']:.1f}")
    print(f"Avg Time: {stats['avg_time']:.1f}s")
    if "avg_quality_score" in stats:
        print(f"Avg Quality Score: {stats['avg_quality_score']:.2f}")
    print(f"\nResults saved to: {results_file}")
    print('='*70)
    
    return output

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Run benchmark evaluation")
    parser.add_argument(
        "--model", "-m",
        type=str,
        default="grok-4-latest",
        choices=["grok-4-latest", "grok-vision-beta"],
        help="Grok model to use"
    )
    parser.add_argument(
        "--queries", "-q",
        type=str,
        default="evaluation/queries.json",
        help="Path to queries file"
    )
    parser.add_argument(
        "--max-queries", "-n",
        type=int,
        default=None,
        help="Maximum number of queries to run"
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="results/benchmark",
        help="Output directory"
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Run benchmark with the deterministic offline client"
    )
    
    args = parser.parse_args()
    
    # Load queries
    queries = load_queries(args.queries)
    
    # Run benchmark
    model = GrokModel(args.model)
    run_benchmark(
        queries,
        model=model,
        max_queries=args.max_queries,
        output_dir=args.output_dir,
        offline=args.offline
    )

if __name__ == "__main__":
    main()
