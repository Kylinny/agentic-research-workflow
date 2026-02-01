# Troubleshooting Guide

## Common Issues and Solutions

### Installation Issues

#### 1. `pip install` fails

**Problem**: Dependencies fail to install

**Solutions**:
```bash
# Update pip
pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v

# Install specific problematic packages separately
pip install sentence-transformers
pip install faiss-cpu
```

#### 2. FAISS installation fails on Mac M1/M2

**Problem**: faiss-cpu incompatible with ARM architecture

**Solution**:
```bash
# Use conda instead
conda install -c pytorch faiss-cpu

# Or use alternative
pip install faiss-cpu==1.7.4
```

#### 3. Sentence-transformers slow to download

**Problem**: Model downloads are large (~400MB)

**Solution**:
```bash
# Pre-download models
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Or use a smaller model (edit tools/hybrid_retrieval.py)
# Change to: 'paraphrase-MiniLM-L3-v2' (60MB)
```

### API Issues

#### 1. "XAI_API_KEY not found"

**Problem**: Environment variable not set

**Solutions**:
```bash
# Create .env file
cp .env.example .env

# Edit .env and add your key
# XAI_API_KEY=your_key_here

# Or export directly
export XAI_API_KEY="your_key_here"
```

#### 2. API connection timeouts

**Problem**: Network issues or API unavailable

**Solutions**:
```bash
# Test connection
python -c "from grok import GrokClient; print(GrokClient().test_connection())"

# Check API status at console.x.ai

# Increase timeout in grok/client.py:
# Add timeout parameter to OpenAI client initialization
```

#### 3. Rate limit errors

**Problem**: Too many requests too quickly

**Solutions**:
```python
# In evaluation/run_benchmark.py, increase delay:
time.sleep(2)  # Instead of time.sleep(1)

# Run fewer queries:
python evaluation/run_benchmark.py --max-queries 5

# Use a different model with higher limits
python main.py --model grok-2-latest --query "your query"
```

#### 4. "Invalid API key" error

**Problem**: Incorrect or expired API key

**Solutions**:
```bash
# Verify your key at console.x.ai
# Make sure no extra spaces or quotes in .env:
XAI_API_KEY=xai-abc123...  # Correct
XAI_API_KEY="xai-abc123..."  # Wrong (remove quotes)
XAI_API_KEY= xai-abc123...  # Wrong (extra space)

# Test with curl:
curl https://api.x.ai/v1/chat/completions \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"grok-beta","messages":[{"role":"user","content":"test"}]}'
```

### Data Issues

#### 1. "Data directory not found"

**Problem**: Datasets haven't been generated

**Solution**:
```bash
# Generate datasets
python scripts/generate_datasets.py

# Verify files created
ls -la data/
# Should see: x_posts.json, research_papers.json, dataset_stats.json
```

#### 2. Dataset generation fails

**Problem**: Permissions or disk space

**Solutions**:
```bash
# Check disk space
df -h

# Create data directory manually
mkdir -p data/embeddings

# Check permissions
chmod 755 data

# Run with verbose output
python scripts/generate_datasets.py
```

#### 3. Embeddings not being created

**Problem**: Sentence-transformers not working

**Solutions**:
```python
# Test embedding creation
python -c "
from tools.hybrid_retrieval import HybridRetrievalTool
tool = HybridRetrievalTool()
tool.load_documents('x_posts')
"

# If fails, reinstall sentence-transformers
pip uninstall sentence-transformers
pip install sentence-transformers
```

### Execution Issues

#### 1. Agent gets stuck in loop

**Problem**: Agent keeps replanning without progress

**Solutions**:
```bash
# Reduce max iterations
python main.py --max-iterations 5 --query "your query"

# Check execution trace in results file
cat results/result_*.json | jq '.execution_trace'

# This is by design if query is ambiguous - agent is trying to resolve
```

#### 2. All tasks fail

**Problem**: Data files not found or corrupted

**Solutions**:
```bash
# Regenerate datasets
python scripts/generate_datasets.py

# Verify JSON is valid
python -c "import json; json.load(open('data/x_posts.json'))"
python -c "import json; json.load(open('data/research_papers.json'))"

# Check file sizes
ls -lh data/*.json
# x_posts.json should be ~500KB
# research_papers.json should be ~300KB
```

#### 3. JSON parsing errors from Grok

**Problem**: Grok returns non-JSON format

**Solutions**:
- Agent has fallback parsing - should recover automatically
- If persists, try different model:
  ```bash
  python main.py --model grok-2-latest --query "your query"
  ```
- Check `raw_response` in results to see what Grok returned

#### 4. Memory errors

**Problem**: System runs out of memory

**Solutions**:
```bash
# Monitor memory usage
htop  # or top on Mac

# Reduce context size in agent initialization
# Edit agent/core.py:
context = ContextManager(max_context_size=4000)  # Default is 8000

# Process fewer documents
# Edit tools/hybrid_retrieval.py:
def search(..., top_k: int = 5):  # Instead of 10
```

### Docker Issues

#### 1. Docker build fails

**Problem**: Network issues or cache problems

**Solutions**:
```bash
# Clear Docker cache
docker system prune -a

# Build without cache
docker-compose build --no-cache

# Build with verbose output
docker-compose build --progress=plain
```

#### 2. Container exits immediately

**Problem**: Missing environment variables

**Solutions**:
```bash
# Check environment
docker-compose config

# Ensure .env file exists
ls -la .env

# Run with explicit env
docker run -e XAI_API_KEY=your_key research-agent python main.py --help
```

#### 3. Volume mount issues

**Problem**: Data not persisting or not accessible

**Solutions**:
```bash
# Check volume mounts
docker-compose ps -a

# Verify permissions
ls -la data/ results/

# Use absolute paths in docker-compose.yml:
volumes:
  - /absolute/path/to/data:/app/data:rw
```

#### 4. Health check fails

**Problem**: Grok client can't connect inside container

**Solutions**:
```bash
# Check container logs
docker-compose logs research-agent

# Test connection manually
docker exec -it research-agent python -c "from grok import GrokClient; print(GrokClient().test_connection())"

# Disable health check temporarily (docker-compose.yml):
# Comment out the HEALTHCHECK line
```

### Performance Issues

#### 1. Very slow execution

**Problem**: Multiple factors could contribute

**Solutions**:
```bash
# Use faster model
python main.py --model grok-2-latest --query "your query"

# Reduce max iterations
python main.py --max-iterations 3 --query "your query"

# Simplify query
# Instead of: "Analyze everything about AI"
# Use: "What are the main AI safety concerns?"

# Check internet connection
ping api.x.ai
```

#### 2. High token usage

**Problem**: Costs accumulating quickly

**Solutions**:
```python
# Reduce context window (agent/context_manager.py):
def __init__(self, max_context_size: int = 4000):  # Instead of 8000

# Use fewer examples in prompts
# Edit grok/prompts.py to be more concise

# Limit result sizes (tools/hybrid_retrieval.py):
if len(result_str) > 1000:  # Instead of 2000
    result_str = result_str[:1000] + "..."
```

#### 3. Embeddings take too long

**Problem**: Encoding large amounts of text

**Solutions**:
```python
# Use smaller embedding model
# In tools/hybrid_retrieval.py:
self.encoder = SentenceTransformer('paraphrase-MiniLM-L3-v2')

# Cache embeddings more aggressively
# Already implemented - if still slow, check disk I/O

# Reduce number of documents
# Edit scripts/generate_datasets.py:
x_posts = generate_x_posts(num_posts=200)  # Instead of 500
papers = generate_research_papers(num_papers=100)  # Instead of 200
```

### Evaluation Issues

#### 1. Benchmark takes too long

**Problem**: Testing too many queries

**Solution**:
```bash
# Test fewer queries
python evaluation/run_benchmark.py --max-queries 5

# Test specific categories
# Edit evaluation/queries.json to comment out queries
```

#### 2. Model comparison fails

**Problem**: One model errors and stops process

**Solution**:
```python
# In evaluation/compare_models.py, wrap in try-except
try:
    result = run_benchmark(...)
except Exception as e:
    print(f"Model {model} failed: {e}")
    continue  # Skip to next model
```

#### 3. Visualization fails

**Problem**: matplotlib errors or display issues

**Solutions**:
```bash
# Install display backend
pip install PyQt5  # or Tkinter

# Or disable visualizations
# Comment out create_visualizations() call in compare_models.py

# Use non-interactive backend (already in code):
matplotlib.use('Agg')
```

### Debugging Tips

#### 1. Enable verbose logging

```python
# In main.py, always use verbose:
result = agent.research(query, verbose=True)

# Check execution trace:
print(json.dumps(result['execution_trace'], indent=2))
```

#### 2. Inspect intermediate results

```python
# In agent/core.py, add print statements:
print(f"Plan: {json.dumps(current_plan, indent=2)}")
print(f"Execution results: {execution_results}")
print(f"Analysis: {analysis}")
```

#### 3. Test components individually

```bash
# Test Grok client
python -c "
from grok import GrokClient, GrokModel
client = GrokClient()
response = client.chat_completion(
    [{'role': 'user', 'content': 'Hello'}],
    model=GrokModel.GROK_BETA
)
print(response)
"

# Test tools
python -c "
from tools import XSearchTool
tool = XSearchTool()
results = tool.search('AI safety')
print(f'Found {len(results)} results')
"

# Test hybrid retrieval
python -c "
from tools import HybridRetrievalTool
tool = HybridRetrievalTool()
results = tool.search('machine learning', 'x_posts', top_k=5)
print(f'Found {len(results)} results')
"
```

### Getting Help

If you continue to experience issues:

1. **Check logs**: Look in `logs/` directory for error details
2. **Review results**: Check `results/` for partial outputs
3. **Verify setup**: Ensure all dependencies installed
4. **Test connection**: Verify API access
5. **Simplify**: Try with simpler query first
6. **Update**: Make sure all packages are latest versions

```bash
pip install --upgrade -r requirements.txt
```

### Known Limitations

1. **Mock Data**: Uses generated data, not real X/research APIs
2. **Sentiment Analysis**: Rule-based, not ML-based
3. **No Caching**: Re-computes embeddings each run
4. **Sequential Execution**: Tasks run one at a time
5. **English Only**: Not tested with non-English text
6. **Token Limits**: May truncate very long contexts

These are intentional trade-offs for the prototype and can be addressed in production versions.

