# Setup Guide

## Quick Start (5 minutes)

### 1. Prerequisites

- Python 3.10 or higher
- pip package manager
- Git
- (Optional) Docker and Docker Compose

### 2. Clone from GitHub

```bash
# Clone the repository
git clone https://github.com/Kylinny/agentic-research-workflow.git
cd agentic-research-workflow

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. API Key Setup

#### Get Your Free Credits

1. Go to [console.x.ai](https://console.x.ai)
2. Create an account (if you don't have one)
3. Navigate to **Manage → Billing** (bottom left sidebar)
4. Click on **Free credits**
5. Click **Redeem promo code**
6. Enter code: **`grok_eng_9a9e9f2a`**
7. You'll receive **$20 in free credits**!

#### Configure API Key

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API key
nano .env  # or use any text editor
```

Add this line to `.env`:
```bash
XAI_API_KEY=your_api_key_from_console
```

### 4. Generate Datasets

```bash
# Generate mock X posts and research papers
python scripts/generate_datasets.py
```

Expected output:
```
Generating X posts dataset...
✓ Generated 500 X posts

Generating research papers dataset...
✓ Generated 200 research papers

==================================================
Dataset Generation Complete!
==================================================
```

### 5. Test the System

```bash
# Test with a simple query
python main.py --query "What are users saying about AI safety on X?"
```

## Detailed Setup

### Environment Variables

Create `.env` file with these configurations:

```bash
# Required
XAI_API_KEY=your_api_key_here

# Optional (with defaults)
XAI_BASE_URL=https://api.x.ai/v1
DEFAULT_GROK_MODEL=grok-beta
MAX_ITERATIONS=10
CONTEXT_WINDOW_SIZE=8000
ENABLE_REPLANNING=true
```

### Verify Installation

#### 1. Check Python packages

```bash
pip list | grep -E "openai|sentence-transformers|faiss"
```

Should show:
- openai >= 1.12.0
- sentence-transformers >= 2.3.0
- faiss-cpu >= 1.7.4

#### 2. Test Grok connection

```bash
python -c "
from grok import GrokClient
client = GrokClient()
if client.test_connection():
    print('✓ Grok API connection successful!')
else:
    print('✗ Connection failed - check API key')
"
```

#### 3. Test data loading

```bash
python -c "
import json
import os

files = ['data/x_posts.json', 'data/research_papers.json']
for f in files:
    if os.path.exists(f):
        data = json.load(open(f))
        print(f'✓ {f}: {len(data)} items')
    else:
        print(f'✗ {f}: not found')
"
```

#### 4. Test tools

```bash
python -c "
from tools import XSearchTool, PaperSearchTool, HybridRetrievalTool

print('Testing XSearchTool...')
x_tool = XSearchTool()
x_results = x_tool.search('AI')
print(f'✓ X Search: {len(x_results)} results')

print('Testing PaperSearchTool...')
paper_tool = PaperSearchTool()
paper_results = paper_tool.search('machine learning')
print(f'✓ Paper Search: {len(paper_results)} results')

print('Testing HybridRetrievalTool...')
hybrid_tool = HybridRetrievalTool()
hybrid_results = hybrid_tool.search('neural networks', 'papers', top_k=5)
print(f'✓ Hybrid Retrieval: {len(hybrid_results)} results')

print('\nAll tools working correctly!')
"
```

## Docker Setup

### Option 1: Docker Compose (Recommended)

```bash
# Build and run
docker-compose up --build

# Or run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Option 2: Docker Only

```bash
# Build image
docker build -t agentic-research .

# Run interactive mode
docker run -it \
  -e XAI_API_KEY=your_key \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/results:/app/results \
  agentic-research \
  python main.py --interactive

# Run single query
docker run \
  -e XAI_API_KEY=your_key \
  -v $(pwd)/results:/app/results \
  agentic-research \
  python main.py --query "Your query here"
```

### Generate Datasets in Docker

```bash
# Using docker-compose profiles
docker-compose --profile setup run dataset-generator

# Or directly
docker run \
  -v $(pwd)/data:/app/data \
  agentic-research \
  python scripts/generate_datasets.py
```

## IDE Setup

### VS Code

1. Install Python extension
2. Select interpreter: `./venv/bin/python`
3. Install recommended extensions:
   - Python
   - Pylance
   - Docker

### PyCharm

1. Open project
2. Configure interpreter: Settings → Project → Python Interpreter
3. Select existing virtualenv: `./venv`

## Troubleshooting Setup

### Issue: "No module named 'grok'"

**Solution**:
```bash
# Ensure you're in project root and venv is activated
pwd  # Should show .../agentic-research-workflow
which python  # Should show .../agentic-research-workflow/venv/bin/python

# Add project to PYTHONPATH if needed
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Issue: "sentence-transformers downloading models"

**Solution**: First run will download embedding models (~400MB). Wait for completion:
```bash
# Pre-download to avoid delays later
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Issue: "Permission denied" on data directory

**Solution**:
```bash
# Fix permissions
chmod 755 data
chmod 644 data/*.json

# Or recreate
rm -rf data
mkdir data
python scripts/generate_datasets.py
```

### Issue: Docker can't find .env file

**Solution**:
```bash
# Ensure .env exists
ls -la .env

# Copy template if missing
cp .env.example .env

# Or pass env vars directly
docker run -e XAI_API_KEY=your_key ...
```

## Next Steps

After setup is complete:

1. **Try Example Queries**
   ```bash
   python main.py --query "What are the main AI safety concerns?"
   python main.py --query "Compare quantum computing research trends"
   ```

2. **Run in Interactive Mode**
   ```bash
   python main.py --interactive
   ```

3. **Run Benchmark Evaluation**
   ```bash
   python evaluation/run_benchmark.py --max-queries 5
   ```

4. **Compare Models**
   ```bash
   python evaluation/compare_models.py --max-queries 5
   ```

5. **Explore Results**
   ```bash
   # Check generated results
   ls -la results/
   
   # View a result
   cat results/result_0.json | jq .
   ```

## Development Setup

For development and contributions:

```bash
# Install development dependencies (optional)
pip install pytest black flake8 mypy

# Run tests (when available)
pytest tests/

# Format code
black .

# Lint
flake8 --max-line-length=100 .
```

## Uninstallation

```bash
# Remove virtual environment
deactivate
rm -rf venv

# Remove generated data
rm -rf data results logs

# Remove Docker images
docker rmi agentic-research-workflow
docker system prune -a
```

## Getting Help

- **Documentation**: See `README.md` and `docs/`
- **Troubleshooting**: See `docs/TROUBLESHOOTING.md`
- **Issues**: Check common issues above

Setup complete! 🎉 You're ready to start researching with your AI agent!

