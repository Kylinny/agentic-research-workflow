"""
Main entry point for the Agentic Research Workflow
"""
import os
import sys
import argparse
import json
from dotenv import load_dotenv
from colorama import Fore, Style, init
from grok import GrokClient, GrokModel
from agent import ResearchAgent

init(autoreset=True)

def load_environment():
    """Load environment variables"""
    load_dotenv()
    
    if not os.getenv("XAI_API_KEY"):
        print(f"{Fore.RED}Error: XAI_API_KEY not found in environment")
        print(f"Please set it in .env file or environment variables{Style.RESET_ALL}")
        sys.exit(1)

def print_result(result: dict):
    """Pretty print research results"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"RESEARCH RESULTS")
    print(f"{'='*70}{Style.RESET_ALL}\n")
    
    print(f"{Fore.YELLOW}Query:{Style.RESET_ALL} {result['query']}\n")
    
    if result["success"]:
        print(f"{Fore.GREEN}Status: SUCCESS{Style.RESET_ALL}\n")
        print(f"{Fore.YELLOW}Answer:{Style.RESET_ALL}\n")
        print(result["answer"])
        print()
    else:
        print(f"{Fore.RED}Status: FAILED{Style.RESET_ALL}\n")
    
    # Statistics
    print(f"\n{Fore.CYAN}{'─'*70}")
    print(f"STATISTICS")
    print(f"{'─'*70}{Style.RESET_ALL}")
    print(f"Model: {result['model_used']}")
    print(f"Iterations: {result['iterations']}")
    print(f"Tasks: {result['successful_tasks']}/{result['total_tasks']} successful")
    print(f"Replans: {result['replans']}")
    
    if result.get("quality_metrics"):
        print(f"\n{Fore.CYAN}Quality Metrics:{Style.RESET_ALL}")
        metrics = result["quality_metrics"]
        print(f"  Completeness: {metrics['completeness']:.2f}")
        print(f"  Coherence: {metrics['coherence']:.2f}")
        print(f"  Evidence Support: {metrics['evidence_support']:.2f}")
        print(f"  Overall Score: {metrics['overall_score']:.2f}")
    
    if result.get("token_usage"):
        print(f"\n{Fore.CYAN}Token Usage:{Style.RESET_ALL}")
        usage = result["token_usage"]
        print(f"  Prompt: {usage.get('prompt_tokens', 0):,}")
        print(f"  Completion: {usage.get('completion_tokens', 0):,}")
        print(f"  Total: {usage.get('total_tokens', 0):,}")
    
    print()

def interactive_mode(agent: ResearchAgent):
    """Run agent in interactive mode"""
    print(f"\n{Fore.GREEN}Interactive Research Mode{Style.RESET_ALL}")
    print("Enter your research queries (or 'quit' to exit)\n")
    
    while True:
        try:
            query = input(f"{Fore.YELLOW}Query > {Style.RESET_ALL}").strip()
            
            if not query:
                continue
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            # Execute research
            result = agent.research(query, verbose=True)
            print_result(result)
            
            # Save result
            output_file = f"results/result_{len(os.listdir('results')) if os.path.exists('results') else 0}.json"
            os.makedirs("results", exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"{Fore.GREEN}✓ Results saved to {output_file}{Style.RESET_ALL}\n")
            
            # Reset for next query
            agent.reset()
            
        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}\n")

def main():
    parser = argparse.ArgumentParser(
        description="Agentic Research Workflow with Grok",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single query
  python main.py --query "What are the latest trends in AI safety?"
  
  # Interactive mode
  python main.py --interactive
  
  # Use different model
  python main.py --model grok-2-latest --query "Your query here"
  
  # Save output to file
  python main.py --query "Your query" --output results/output.json
        """
    )
    
    parser.add_argument(
        "--query", "-q",
        type=str,
        help="Research query to execute"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    
    parser.add_argument(
        "--model", "-m",
        type=str,
        default="grok-4-latest",
        choices=["grok-4-latest", "grok-vision-beta"],
        help="Grok model variant to use"
    )
    
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=10,
        help="Maximum number of agent iterations"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file for results (JSON)"
    )
    
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data",
        help="Directory containing data files"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        default=True,
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Load environment
    load_environment()
    
    # Validate data directory
    if not os.path.exists(args.data_dir):
        print(f"{Fore.YELLOW}Warning: Data directory '{args.data_dir}' not found")
        print(f"Run 'python scripts/generate_datasets.py' to create datasets{Style.RESET_ALL}\n")
    
    # Initialize agent
    try:
        model = GrokModel(args.model)
        print(f"{Fore.CYAN}Initializing Research Agent...{Style.RESET_ALL}")
        agent = ResearchAgent(
            model=model,
            max_iterations=args.max_iterations,
            data_dir=args.data_dir
        )
    except Exception as e:
        print(f"{Fore.RED}Failed to initialize agent: {e}{Style.RESET_ALL}")
        return 1
    
    # Execute based on mode
    if args.interactive:
        interactive_mode(agent)
    elif args.query:
        result = agent.research(args.query, verbose=args.verbose)
        print_result(result)
        
        # Save output if specified
        if args.output:
            os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"{Fore.GREEN}✓ Results saved to {args.output}{Style.RESET_ALL}")
    else:
        parser.print_help()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

