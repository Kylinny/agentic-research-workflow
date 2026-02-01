# Technical Documentation

## Architecture Overview

The Agentic Research Workflow is built on a modular architecture that enables autonomous research through iterative planning, execution, and refinement.

### Core Components

#### 1. Grok Integration Layer (`grok/`)

**Purpose**: Interface with X.AI's Grok API for reasoning and decision-making.

**Components**:
- `client.py`: Robust API client with retry logic, token counting, and error handling
- `models.py`: Model variant configurations (grok-beta, grok-2-latest, etc.)
- `prompts.py`: Optimized prompt templates for planning, analysis, and synthesis

**Key Features**:
- Exponential backoff for retries
- Token-aware context management
- Support for multiple model variants
- Structured output parsing

**Design Decisions**:
- Used OpenAI-compatible client for consistency
- Implemented retry logic to handle transient failures
- Separated prompts into dedicated module for maintainability

#### 2. Agent Core (`agent/`)

**Purpose**: Implements the main agentic workflow loop.

##### 2.1 Planner (`planner.py`)

**Responsibilities**:
- Decompose complex queries into sub-tasks
- Select appropriate tools for each task
- Create dependency graphs
- Replan when encountering issues

**Algorithm**:
```python
def create_plan(query, context):
    1. Analyze query requirements
    2. Identify data sources needed
    3. Break into atomic tasks
    4. Assign tools to tasks
    5. Determine dependencies
    6. Estimate challenges
    return structured_plan
```

**Trade-offs**:
- **Pro**: Flexible planning adapts to query complexity
- **Pro**: Dependencies ensure correct execution order
- **Con**: Planning adds latency (mitigated with caching)
- **Con**: May over-decompose simple queries

##### 2.2 Executor (`executor.py`)

**Responsibilities**:
- Execute planned tasks
- Respect task dependencies
- Handle tool failures gracefully
- Aggregate results

**Execution Strategy**:
- Topological sort for dependency resolution
- Parallel execution where possible (future enhancement)
- Graceful degradation on partial failures

**Tool Mapping**:
```python
{
    "x_search": XSearchTool,
    "paper_search": PaperSearchTool,
    "sentiment_analysis": SentimentAnalysisTool,
    "citation_tracker": CitationTrackerTool,
    "hybrid_retrieval": HybridRetrievalTool
}
```

##### 2.3 Analyzer (`analyzer.py`)

**Responsibilities**:
- Evaluate result quality
- Detect ambiguities and gaps
- Determine if replanning is needed
- Synthesize final answers

**Quality Metrics**:
- **Completeness**: Coverage of query aspects
- **Coherence**: Logical flow and structure
- **Evidence Support**: Citation density
- **Overall Score**: Weighted combination

**Replanning Triggers**:
- Quality score < 5.0
- Completeness < 5.0
- Explicit contradictions detected
- No successful tool executions

##### 2.4 Context Manager (`context_manager.py`)

**Responsibilities**:
- Maintain conversation history
- Track execution trace
- Manage token budget
- Extract key insights

**Context Strategy**:
- Keep last N steps in memory
- Summarize older context
- Prioritize relevant history
- Truncate to token limits

**Memory Structure**:
```python
{
    "history": [...],           # Full history
    "current_plan": {...},      # Active plan
    "execution_trace": [...],   # Step-by-step record
    "key_insights": [...]       # Extracted insights
}
```

##### 2.5 Research Agent (`core.py`)

**Main Loop**:
```python
while iteration < max_iterations:
    1. Plan (or replan if needed)
    2. Execute tasks respecting dependencies
    3. Analyze results
    4. Check quality and completeness
    5. Decide: continue, replan, or finish
    
return synthesized_answer
```

**Termination Conditions**:
- Quality threshold met (score ≥ 7.0)
- Max iterations reached
- No progress (all tasks failing)
- Explicit user interruption

#### 3. Tools Layer (`tools/`)

**Purpose**: Specialized tools for data retrieval and analysis.

##### 3.1 Hybrid Retrieval (`hybrid_retrieval.py`)

**Algorithm**:
```
score = α × semantic_similarity + β × keyword_match

Where:
- semantic_similarity: cosine similarity of embeddings
- keyword_match: term overlap + exact match bonus
- α, β: configurable weights (default: 0.6, 0.4)
```

**Implementation**:
- Sentence-BERT for embeddings (all-MiniLM-L6-v2)
- FAISS for vector indexing (when dataset scales)
- Caching to avoid re-encoding

**Trade-offs**:
- **Pro**: Balances semantic understanding with precision
- **Pro**: Handles synonym variations
- **Con**: Slower than pure keyword search
- **Con**: Embedding quality depends on model

##### 3.2 X Search (`x_search.py`)

**Features**:
- Content search with filters
- Thread reconstruction
- Conversation tree building
- Sentiment trend analysis
- Influencer identification

**Optimization**:
- Index by topic and timestamp
- Lazy loading of threads
- Cached engagement metrics

##### 3.3 Paper Search (`paper_search.py`)

**Features**:
- Multi-field search (title, abstract, keywords)
- Related paper discovery
- Field trend analysis
- Methodology comparison

**Search Strategy**:
1. Full-text search across fields
2. Apply filters (year, venue, field)
3. Rank by relevance
4. Expand with related papers

##### 3.4 Citation Tracker (`citations.py`)

**Features**:
- Citation network construction
- Influential paper identification
- Citation chain tracing
- Impact metric calculation

**Graph Algorithms**:
- DFS for citation chains
- BFS for network expansion
- PageRank-inspired influence scoring

**Impact Metrics**:
```python
impact_score = 
    direct_citations × 1.0 +
    second_order_citations × 0.1 +
    citation_velocity × 5.0
```

##### 3.5 Sentiment Analysis (`sentiment.py`)

**Approach**: Rule-based with lexicon matching

**Features**:
- Positive/negative/neutral classification
- Sarcasm detection
- Thread sentiment evolution
- Conversation agreement analysis

**Why Rule-Based**:
- **Pro**: Fast and interpretable
- **Pro**: No model download required
- **Pro**: Predictable behavior
- **Con**: Lower accuracy than transformers
- **Future**: Could swap with VADER or fine-tuned model

#### 4. Data Layer

**Mock Data Generation**:
- Realistic X posts with threads and replies
- Research papers with citations
- Temporal patterns and trends
- Noise and ambiguity for robustness testing

**Data Quality**:
- Diverse topics (16 domains)
- Realistic engagement metrics
- Citation networks with varying density
- Sentiment distribution matching real-world

### Workflow Visualization

```
┌─────────────────┐
│  User Query     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Planning Phase                         │
│  • Grok analyzes query                  │
│  • Decomposes into sub-tasks            │
│  • Selects tools                        │
│  • Creates execution plan               │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Execution Phase                        │
│  • Execute tasks in dependency order    │
│  • Tools retrieve relevant data         │
│  • Results aggregated                   │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Analysis Phase                         │
│  • Grok evaluates results               │
│  • Checks quality & completeness        │
│  • Identifies gaps/ambiguities          │
└────────┬────────────────────────────────┘
         │
         ├──► Needs Replanning? ──Yes──┐
         │                              │
         No                             │
         │                              │
         ▼                              │
┌─────────────────────────────────────┐  │
│  Sufficient Results?                 │  │
│  • Quality ≥ 7.0?                   │  │
│  • Completeness ≥ 7.0?              │  │
└────────┬────────────────────────────┘  │
         │                               │
         Yes                             │
         │                               │
         ▼                               │
┌─────────────────────────────────────┐  │
│  Synthesis Phase                    │  │
│  • Grok synthesizes final answer    │  │
│  • Cites sources                    │  │
│  • Assesses confidence              │  │
└────────┬────────────────────────────┘  │
         │                               │
         ▼                               │
┌─────────────────────────────────────┐  │
│  Final Result                       │  │
└─────────────────────────────────────┘  │
         ▲                               │
         │                               │
         └───────────────────────────────┘
```

### Key Design Patterns

#### 1. Chain of Responsibility
- Request flows through planner → executor → analyzer
- Each component decides whether to continue or replan

#### 2. Strategy Pattern
- Different tools implement common interface
- Executor selects appropriate tool at runtime

#### 3. Observer Pattern
- Context manager observes all agent actions
- Maintains execution trace for analysis

#### 4. Template Method
- Grok prompts follow structured templates
- Ensures consistent output format

### Performance Considerations

#### Latency
- **Planning**: 2-5s per plan
- **Tool Execution**: 0.1-1s per tool
- **Analysis**: 2-4s per iteration
- **Synthesis**: 3-6s
- **Total**: ~30-60s for typical query

#### Token Usage
- **Planning**: ~1000-2000 tokens
- **Analysis**: ~800-1500 tokens
- **Synthesis**: ~1500-3000 tokens
- **Context**: ~500-1000 tokens
- **Total per iteration**: ~4000-8000 tokens

#### Scalability
- **Current**: Handles 100s of documents
- **With FAISS**: Could scale to millions
- **Bottleneck**: Grok API calls (sequential)
- **Future**: Parallel tool execution

### Error Handling

#### Levels of Graceful Degradation

1. **Task Level**: Individual task failure doesn't stop agent
2. **Iteration Level**: Failed iteration triggers replanning
3. **Agent Level**: Multiple failures return partial results
4. **API Level**: Retry with exponential backoff

#### Error Recovery Strategies

```python
if task_fails:
    retry_with_different_params()
    
if all_tasks_fail:
    replan_with_alternative_approach()
    
if planning_fails:
    use_fallback_simple_plan()
    
if api_unavailable:
    return_cached_results_or_error()
```

### Testing Strategy

#### Unit Tests (Future Work)
- Test each tool independently
- Mock Grok API responses
- Verify prompt parsing

#### Integration Tests
- Test full agent workflow
- Use small dataset subset
- Verify end-to-end execution

#### Benchmark Tests
- 40 diverse queries
- Multiple model variants
- Measure quality and efficiency

### Future Enhancements

1. **Parallel Execution**: Run independent tasks concurrently
2. **Caching**: Cache tool results for similar queries
3. **Streaming**: Stream results as they arrive
4. **Fine-tuning**: Custom prompts per domain
5. **Human-in-the-Loop**: Allow user intervention
6. **Multi-Modal**: Support images, videos
7. **Real-Time Data**: Connect to live X API
8. **Advanced NLP**: Use transformers for sentiment
9. **Query Optimization**: Learn from past queries
10. **Distributed**: Scale across multiple workers

