# Agentic Research Workflow with Grok

[![GitHub](https://img.shields.io/badge/GitHub-Kylinny%2Fagentic--research--workflow-blue?logo=github)](https://github.com/Kylinny/agentic-research-workflow)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![Grok](https://img.shields.io/badge/Grok-4--latest-purple)](https://x.ai/)

A sophisticated autonomous multi-step agentic workflow system using Grok as the central reasoner for complex research on simulated X data and research papers.

**🔗 GitHub Repository**: https://github.com/Kylinny/agentic-research-workflow

## Overview

This system implements an advanced agentic workflow that:
- **Plans and decomposes** complex research queries into manageable sub-tasks
- **Selects and executes** appropriate tools based on task requirements
- **Analyzes and refines** results through iterative loops
- **Handles ambiguity** with Grok-driven replanning
- **Manages context** across multiple reasoning steps
- **Synthesizes insights** from diverse data sources

## Features

### 🤖 Agentic Workflow
- Iterative loop: plan → decompose → select tools → analyze → refine → summarize
- Context-aware decision making with multi-step memory
- Adaptive replanning when encountering ambiguous or insufficient results
- Tool chaining for complex multi-hop reasoning

### 📊 Mock Datasets
- **X (Twitter) Data**: Real-time style posts with replies, threads, timestamps, and engagement metrics
- **Research Papers**: Structured documents with abstracts, methodologies, results, and citations
- Realistic noise, sarcasm detection challenges, and multilingual content

### 🔍 Hybrid Retrieval System
- Semantic search using sentence transformers
- Keyword-based retrieval for precise matching
- FAISS-powered vector indexing for scalability
- Cross-document analysis and citation tracking

### 🧠 Grok Integration
- Multiple model variants (grok-beta, grok-2-latest, etc.)
- Optimized prompting for planning and reasoning
- Error handling and retry logic
- Token-aware context management

### 📈 Evaluation Framework
- 20-40 complex research queries
- Metrics: completion rate, step efficiency, answer quality
- Comparative analysis across Grok model variants
- Automated benchmarking

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/Kylinny/agentic-research-workflow.git
cd agentic-research-workflow

# Set up your API key
cp .env.example .env
# Edit .env and add your X.AI API key

# Build and run
docker-compose up --build
```

### Local Installation

```bash
# Clone the repository
git clone https://github.com/Kylinny/agentic-research-workflow.git
cd agentic-research-workflow

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your X.AI API key

# Generate datasets
python scripts/generate_datasets.py

# Run the agent
python main.py --query "What are the latest trends in AI safety research?"
```

## Usage

### Running the Agent

```bash
# Interactive mode
python main.py --interactive

# Single query
python main.py --query "Analyze the sentiment around recent AI regulation discussions"

# Batch evaluation
python evaluation/run_benchmark.py

# Compare models
python evaluation/compare_models.py
```

### Example Queries

```bash
# X Data Analysis
python main.py --query "What are users saying about climate change? Identify key influencers and sentiment trends over time."

# Research Paper Analysis
python main.py --query "Compare methodologies used in transformer architecture papers from 2017-2023. What are the key innovations?"

# Cross-domain
python main.py --query "How does public discourse on X about quantum computing align with academic research?"
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│              User Query                         │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│         Grok Planning Agent                     │
│  • Query decomposition                          │
│  • Sub-task generation                          │
│  • Tool selection                               │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│         Tool Execution Layer                    │
│  • X Data Search    • Paper Search              │
│  • Sentiment Analysis • Citation Tracker        │
│  • Thread Analyzer  • Hybrid Retrieval          │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│        Grok Analysis & Refinement               │
│  • Result synthesis                             │
│  • Ambiguity detection                          │
│  • Replanning if needed                         │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│         Context Manager                         │
│  • Multi-step memory                            │
│  • Relevant history retention                   │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│         Final Synthesis                         │
│  • Comprehensive summary                        │
│  • Source citations                             │
│  • Confidence scores                            │
└─────────────────────────────────────────────────┘
```

## Project Structure

```
Xai/
├── agent/
│   ├── __init__.py
│   ├── core.py              # Main agent loop
│   ├── planner.py           # Task decomposition & planning
│   ├── executor.py          # Tool execution
│   ├── analyzer.py          # Result analysis & refinement
│   └── context_manager.py   # Context & memory management
├── grok/
│   ├── __init__.py
│   ├── client.py            # Grok API client
│   ├── prompts.py           # Optimized prompts
│   └── models.py            # Model configurations
├── tools/
│   ├── __init__.py
│   ├── x_search.py          # X data retrieval
│   ├── paper_search.py      # Research paper search
│   ├── sentiment.py         # Sentiment analysis
│   ├── citations.py         # Citation tracking
│   └── hybrid_retrieval.py  # Hybrid search engine
├── data/
│   ├── x_posts.json         # Generated X data
│   ├── research_papers.json # Generated papers
│   └── embeddings/          # Vector indices
├── evaluation/
│   ├── queries.json         # Test queries
│   ├── run_benchmark.py     # Evaluation script
│   ├── compare_models.py    # Model comparison
│   └── metrics.py           # Evaluation metrics
├── scripts/
│   └── generate_datasets.py # Dataset generation
├── Dockerfile
├── docker-compose.yml
├── main.py
├── requirements.txt
└── README.md
```

## Evaluation Metrics

The system tracks:
- **Completion Rate**: % of queries successfully answered
- **Step Efficiency**: Average steps per query
- **Answer Quality**: Relevance, coherence, citation accuracy
- **Replanning Rate**: Frequency of adaptive replanning
- **Context Utilization**: Effective use of conversation history

## Troubleshooting

See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for common issues and solutions.

## Documentation

- [Technical Documentation](docs/TECHNICAL.md) - Architecture and design decisions
- [Troubleshooting Guide](docs/TROUBLESHOOTING.md) - Common issues and solutions

## License

MIT License - See LICENSE file for details.

## Promo Code

Use promo code `grok_eng_9a9e9f2a` on console.x.ai for $20 in free credits.

