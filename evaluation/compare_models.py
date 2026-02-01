"""
Compare multiple Grok model variants on benchmark queries
"""
import json
import os
import sys
from typing import List, Dict
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grok import GrokModel
from evaluation.run_benchmark import run_benchmark, load_queries

def compare_models(
    models: List[GrokModel],
    queries: List[Dict],
    max_queries: int = 10,
    output_dir: str = "results/comparison"
):
    """
    Compare multiple Grok models on the same queries
    
    Args:
        models: List of Grok models to compare
        queries: List of query dicts
        max_queries: Maximum queries to test
        output_dir: Output directory
    """
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Comparing {len(models)} models on {min(max_queries, len(queries))} queries...\n")
    
    all_results = {}
    
    for model in models:
        print(f"\n{'='*70}")
        print(f"Testing {model.display_name}")
        print('='*70)
        
        result = run_benchmark(
            queries,
            model=model,
            max_queries=max_queries,
            output_dir=output_dir
        )
        
        all_results[model.value] = result
    
    # Create comparison report
    comparison = create_comparison_report(all_results)
    
    # Save comparison
    comparison_file = os.path.join(output_dir, "model_comparison.json")
    with open(comparison_file, 'w') as f:
        json.dump(comparison, f, indent=2)
    
    # Create visualizations
    create_visualizations(comparison, output_dir)
    
    # Print summary
    print_comparison_summary(comparison)
    
    return comparison

def create_comparison_report(all_results: Dict) -> Dict:
    """Create structured comparison report"""
    comparison = {
        "models": list(all_results.keys()),
        "metrics": {}
    }
    
    # Extract metrics for each model
    for model, result in all_results.items():
        stats = result["statistics"]
        
        comparison["metrics"][model] = {
            "completion_rate": stats["completion_rate"],
            "avg_iterations": stats["avg_iterations"],
            "avg_tasks": stats["avg_tasks"],
            "avg_replans": stats["avg_replans"],
            "avg_time": stats["avg_time"],
            "avg_quality_score": stats.get("avg_quality_score", 0),
            "successful": stats["successful"],
            "failed": stats["failed"]
        }
    
    # Calculate rankings
    metrics_to_rank = [
        ("completion_rate", True),  # Higher is better
        ("avg_quality_score", True),
        ("avg_time", False),  # Lower is better
        ("avg_iterations", False)
    ]
    
    comparison["rankings"] = {}
    for metric, higher_better in metrics_to_rank:
        values = [(model, data[metric]) 
                 for model, data in comparison["metrics"].items()]
        values.sort(key=lambda x: x[1], reverse=higher_better)
        comparison["rankings"][metric] = [model for model, _ in values]
    
    return comparison

def create_visualizations(comparison: Dict, output_dir: str):
    """Create comparison visualizations"""
    try:
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
        
        metrics = comparison["metrics"]
        models = list(metrics.keys())
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Grok Model Comparison', fontsize=16, fontweight='bold')
        
        # 1. Completion Rate
        ax = axes[0, 0]
        completion_rates = [metrics[m]["completion_rate"] * 100 for m in models]
        ax.bar(models, completion_rates, color='steelblue')
        ax.set_ylabel('Completion Rate (%)')
        ax.set_title('Task Completion Rate')
        ax.set_ylim(0, 100)
        for i, v in enumerate(completion_rates):
            ax.text(i, v + 2, f'{v:.1f}%', ha='center')
        
        # 2. Quality Score
        ax = axes[0, 1]
        quality_scores = [metrics[m]["avg_quality_score"] for m in models]
        ax.bar(models, quality_scores, color='green')
        ax.set_ylabel('Quality Score')
        ax.set_title('Average Quality Score')
        ax.set_ylim(0, 1)
        for i, v in enumerate(quality_scores):
            ax.text(i, v + 0.02, f'{v:.2f}', ha='center')
        
        # 3. Execution Time
        ax = axes[1, 0]
        times = [metrics[m]["avg_time"] for m in models]
        ax.bar(models, times, color='coral')
        ax.set_ylabel('Time (seconds)')
        ax.set_title('Average Execution Time')
        for i, v in enumerate(times):
            ax.text(i, v + max(times)*0.02, f'{v:.1f}s', ha='center')
        
        # 4. Agent Efficiency
        ax = axes[1, 1]
        x = range(len(models))
        width = 0.25
        iterations = [metrics[m]["avg_iterations"] for m in models]
        tasks = [metrics[m]["avg_tasks"] for m in models]
        replans = [metrics[m]["avg_replans"] for m in models]
        
        ax.bar([i - width for i in x], iterations, width, label='Iterations', color='skyblue')
        ax.bar(x, tasks, width, label='Tasks', color='lightgreen')
        ax.bar([i + width for i in x], replans, width, label='Replans', color='salmon')
        ax.set_ylabel('Count')
        ax.set_title('Agent Efficiency Metrics')
        ax.set_xticks(x)
        ax.set_xticklabels(models)
        ax.legend()
        
        plt.tight_layout()
        
        viz_file = os.path.join(output_dir, "model_comparison.png")
        plt.savefig(viz_file, dpi=300, bbox_inches='tight')
        print(f"\n✓ Visualization saved to {viz_file}")
        
    except Exception as e:
        print(f"Warning: Could not create visualizations: {e}")

def print_comparison_summary(comparison: Dict):
    """Print comparison summary"""
    print(f"\n{'='*70}")
    print("MODEL COMPARISON SUMMARY")
    print('='*70)
    
    metrics = comparison["metrics"]
    
    # Create comparison table
    print(f"\n{'Model':<20} {'Complete%':<12} {'Quality':<10} {'Time(s)':<10} {'Iters':<8}")
    print('-'*70)
    
    for model in comparison["models"]:
        m = metrics[model]
        print(f"{model:<20} {m['completion_rate']*100:>10.1f}% "
              f"{m['avg_quality_score']:>9.2f} "
              f"{m['avg_time']:>9.1f} "
              f"{m['avg_iterations']:>7.1f}")
    
    print('\n' + '='*70)
    print("RANKINGS")
    print('='*70)
    
    rankings = comparison["rankings"]
    
    print("\n🏆 Best Completion Rate:")
    for i, model in enumerate(rankings["completion_rate"][:3], 1):
        rate = metrics[model]["completion_rate"] * 100
        print(f"  {i}. {model}: {rate:.1f}%")
    
    print("\n🏆 Best Quality Score:")
    for i, model in enumerate(rankings["avg_quality_score"][:3], 1):
        score = metrics[model]["avg_quality_score"]
        print(f"  {i}. {model}: {score:.2f}")
    
    print("\n⚡ Fastest Execution:")
    for i, model in enumerate(rankings["avg_time"][:3], 1):
        time_val = metrics[model]["avg_time"]
        print(f"  {i}. {model}: {time_val:.1f}s")
    
    print('\n' + '='*70)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Compare Grok model variants")
    parser.add_argument(
        "--models", "-m",
        nargs="+",
        default=["grok-4-latest"],
        help="Models to compare"
    )
    parser.add_argument(
        "--max-queries", "-n",
        type=int,
        default=10,
        help="Number of queries to test"
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="results/comparison",
        help="Output directory"
    )
    
    args = parser.parse_args()
    
    # Convert model names to GrokModel objects
    models = [GrokModel(m) for m in args.models]
    
    # Load queries
    queries = load_queries()
    
    # Run comparison
    compare_models(
        models,
        queries,
        max_queries=args.max_queries,
        output_dir=args.output_dir
    )

if __name__ == "__main__":
    main()

