"""
Quick test to verify all imports work
"""
import sys

def test_imports():
    """Test that all modules can be imported"""
    errors = []
    
    # Test Grok imports
    try:
        from grok import GrokClient, GrokModel
        print("✓ Grok imports successful")
    except Exception as e:
        errors.append(f"✗ Grok import failed: {e}")
    
    # Test Agent imports
    try:
        from agent import ResearchAgent, AgentPlanner, ToolExecutor, ResultAnalyzer, ContextManager
        print("✓ Agent imports successful")
    except Exception as e:
        errors.append(f"✗ Agent import failed: {e}")
    
    # Test Tools imports
    try:
        from tools import XSearchTool, PaperSearchTool, SentimentAnalysisTool, CitationTrackerTool, HybridRetrievalTool
        print("✓ Tools imports successful")
    except Exception as e:
        errors.append(f"✗ Tools import failed: {e}")
    
    # Test data files exist
    import os
    data_files = ['data/x_posts.json', 'data/research_papers.json', 'data/dataset_stats.json']
    for file in data_files:
        if os.path.exists(file):
            print(f"✓ {file} exists")
        else:
            errors.append(f"✗ {file} not found")
    
    # Print summary
    print("\n" + "="*50)
    if errors:
        print("ERRORS FOUND:")
        for error in errors:
            print(f"  {error}")
        return False
    else:
        print("ALL TESTS PASSED!")
        print("System is ready to use.")
        return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)

