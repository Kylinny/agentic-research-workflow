# System Architecture

## High-Level Overview

```
┌───────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                         │
│  CLI / Interactive Mode / Benchmark Runner / API (future)    │
└───────────────────────────┬───────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────┐
│                     RESEARCH AGENT CORE                       │
│                      (agent/core.py)                          │
│                                                               │
│  Orchestrates: Plan → Execute → Analyze → Refine Loop        │
└───┬──────────────┬──────────────┬──────────────┬─────────────┘
    │              │              │              │
    ▼              ▼              ▼              ▼
┌─────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐
│ PLANNER │  │ EXECUTOR │  │ ANALYZER │  │ CONTEXT MGR    │
│         │  │          │  │          │  │                │
│ Creates │  │ Runs     │  │ Evaluates│  │ Maintains      │
│ plans   │  │ tools    │  │ quality  │  │ history &      │
│         │  │          │  │          │  │ memory         │
└────┬────┘  └────┬─────┘  └────┬─────┘  └────────────────┘
     │            │             │
     │            │             │
     └────────────┼─────────────┘
                  │
        Uses Grok for reasoning
                  │
                  ▼
     ┌────────────────────────┐
     │   GROK API CLIENT      │
     │   (grok/client.py)     │
     │                        │
     │ • Multi-model support  │
     │ • Retry logic          │
     │ • Token management     │
     └────────┬───────────────┘
              │
              ▼
     ┌────────────────────────┐
     │   X.AI Grok API        │
     │   api.x.ai/v1          │
     └────────────────────────┘
```

## Agent Workflow Loop

```
┌──────────────┐
│ Start: Query │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│ 1. PLANNING PHASE                    │
│                                      │
│ ┌────────────────────────────────┐  │
│ │ Grok Planner                   │  │
│ │ • Analyze query                │  │
│ │ • Decompose into sub-tasks     │  │
│ │ • Select appropriate tools     │  │
│ │ • Create dependency graph      │  │
│ │ • Identify potential challenges│  │
│ └────────────────────────────────┘  │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ 2. EXECUTION PHASE                   │
│                                      │
│ ┌────────────────────────────────┐  │
│ │ Tool Executor                  │  │
│ │                                │  │
│ │ Execute in order:              │  │
│ │ ┌───────────────────────────┐ │  │
│ │ │ ○ X Search Tool           │ │  │
│ │ │ ○ Paper Search Tool       │ │  │
│ │ │ ○ Hybrid Retrieval        │ │  │
│ │ │ ○ Sentiment Analysis      │ │  │
│ │ │ ○ Citation Tracker        │ │  │
│ │ └───────────────────────────┘ │  │
│ │                                │  │
│ │ Respects dependencies          │  │
│ │ Aggregates results             │  │
│ └────────────────────────────────┘  │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ 3. ANALYSIS PHASE                    │
│                                      │
│ ┌────────────────────────────────┐  │
│ │ Grok Analyzer                  │  │
│ │ • Evaluate result quality      │  │
│ │ • Check completeness           │  │
│ │ • Identify gaps/ambiguities    │  │
│ │ • Detect contradictions        │  │
│ │ • Extract key insights         │  │
│ └────────────────────────────────┘  │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ 4. DECISION PHASE                    │
│                                      │
│      ┌─────────────────┐             │
│      │ Needs Replan?   │             │
│      └────┬──────┬─────┘             │
│          Yes     No                  │
│           │       │                  │
│           │       ▼                  │
│           │  ┌─────────────────┐    │
│           │  │ Good Quality?   │    │
│           │  └────┬──────┬─────┘    │
│           │      Yes     No          │
│           │       │      │           │
│           ▼       ▼      │           │
│      ┌────────┐  ┌──────┐           │
│      │ Replan │  │Finish│           │
│      └───┬────┘  └──┬───┘           │
│          │          │                │
│          └──────────┼────────►Loop  │
│                     │                │
└─────────────────────┼────────────────┘
                      │
                      ▼
┌──────────────────────────────────────┐
│ 5. SYNTHESIS PHASE                   │
│                                      │
│ ┌────────────────────────────────┐  │
│ │ Grok Synthesizer               │  │
│ │ • Combine all insights         │  │
│ │ • Resolve contradictions       │  │
│ │ • Cite sources                 │  │
│ │ • Assess confidence            │  │
│ │ • Create comprehensive report  │  │
│ └────────────────────────────────┘  │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────┐
│ Final Answer │
└──────────────┘
```

## Tool Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        TOOL LAYER                           │
└─────────────────────────────────────────────────────────────┘
     │              │              │              │
     ▼              ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐
│ X Search │  │  Paper   │  │ Sentiment│  │  Citation    │
│   Tool   │  │  Search  │  │ Analysis │  │   Tracker    │
│          │  │   Tool   │  │   Tool   │  │              │
│ • Search │  │          │  │          │  │ • Networks   │
│ • Threads│  │ • Search │  │ • Analyze│  │ • Impact     │
│ • Replies│  │ • Trends │  │ • Threads│  │ • Chains     │
│ • Influenc│ │ • Compare│  │ • Polariz│  │ • Common     │
└────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬───────┘
     │              │              │               │
     └──────────────┴──────────────┴───────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   Hybrid Retrieval     │
              │                        │
              │  Semantic (60%) +      │
              │  Keyword (40%)         │
              │                        │
              │ ┌────────────────────┐ │
              │ │ Sentence-BERT      │ │
              │ │ Embeddings         │ │
              │ └────────────────────┘ │
              └────────┬───────────────┘
                       │
                       ▼
              ┌────────────────────────┐
              │    DATA SOURCES        │
              │                        │
              │ • X Posts (1,604)      │
              │ • Research Papers(200) │
              │ • Embeddings Cache     │
              └────────────────────────┘
```

## Data Flow

```
User Query: "Compare AI safety discourse on X with academic research"
     │
     ▼
[PLANNER] Analyzes query
     │
     ├─► Sub-task 1: Search X posts about AI safety
     ├─► Sub-task 2: Search research papers on AI safety
     ├─► Sub-task 3: Sentiment analysis on X posts
     ├─► Sub-task 4: Extract key themes from papers
     └─► Sub-task 5: Compare and synthesize
     │
     ▼
[EXECUTOR] Runs tools
     │
     ├─► XSearchTool → Returns 15 X posts
     ├─► PaperSearchTool → Returns 8 papers
     ├─► SentimentAnalysisTool → Analyzes 15 posts
     ├─► PaperSearchTool.analyze_themes → Extracts themes
     └─► Results aggregated
     │
     ▼
[ANALYZER] Evaluates
     │
     ├─► Quality: 8/10 ✓
     ├─► Completeness: 7/10 ✓
     ├─► Gaps: None critical
     └─► Decision: Proceed to synthesis
     │
     ▼
[SYNTHESIZER] Creates answer
     │
     └─► Comprehensive report with:
         • Executive summary
         • X sentiment trends (positive, mixed concerns)
         • Academic focus areas (technical solutions, ethics)
         • Key differences identified
         • Citations from both sources
         • Confidence assessment
```

## Context Management

```
┌────────────────────────────────────────────────────────┐
│              CONTEXT MANAGER                           │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │ Execution Trace                              │    │
│  │ ┌──────────────────────────────────────┐    │    │
│  │ │ Step 1: Plan created (3 tasks)       │    │    │
│  │ │ Step 2: X search executed            │    │    │
│  │ │ Step 3: Paper search executed        │    │    │
│  │ │ Step 4: Analysis complete            │    │    │
│  │ │ Step 5: Synthesis started            │    │    │
│  │ └──────────────────────────────────────┘    │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │ Key Insights                                 │    │
│  │ • AI safety concerns focus on alignment      │    │
│  │ • Academic research emphasizes technical...  │    │
│  │ • Public discourse more emotional...         │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │ Current Plan                                 │    │
│  │ Task 1: ✓ Complete                          │    │
│  │ Task 2: ✓ Complete                          │    │
│  │ Task 3: → In Progress                        │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  Token Budget: 2,341 / 8,000 used                    │
└────────────────────────────────────────────────────────┘
```

## Grok Integration

```
┌────────────────────────────────────────────────────────┐
│                  GROK CLIENT                           │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │ Model Selection                              │    │
│  │ • grok-beta (default)                        │    │
│  │ • grok-2-latest                              │    │
│  │ • grok-2-1212                                │    │
│  │ • grok-vision-beta                           │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │ Features                                     │    │
│  │ • Retry with exponential backoff             │    │
│  │ • Token counting and management              │    │
│  │ • Structured output parsing                  │    │
│  │ • Error handling and recovery                │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │ Prompt Templates                             │    │
│  │ • PLANNER_SYSTEM_PROMPT                      │    │
│  │ • ANALYZER_SYSTEM_PROMPT                     │    │
│  │ • SYNTHESIZER_SYSTEM_PROMPT                  │    │
│  │ • Dynamic prompt construction                │    │
│  └──────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────┘
                         │
                         ▼
                  [X.AI API]
```

## Evaluation Pipeline

```
┌─────────────────────────────────────────────────┐
│         EVALUATION FRAMEWORK                    │
└─────────────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌──────────────┐       ┌──────────────────┐
│  Benchmark   │       │ Model Comparison │
│   Runner     │       │                  │
│              │       │ Compare 3+ models│
│ 40 queries   │       │ on same queries  │
│ All models   │       │                  │
└──────┬───────┘       └────────┬─────────┘
       │                        │
       └────────────┬───────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │    Metrics Computed    │
        │                        │
        │ • Completion rate      │
        │ • Step efficiency      │
        │ • Quality scores       │
        │ • Token usage          │
        │ • Execution time       │
        │ • Replanning frequency │
        └───────────┬────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │   Results & Viz        │
        │                        │
        │ • JSON reports         │
        │ • Comparison charts    │
        │ • Rankings             │
        │ • Statistical analysis │
        └────────────────────────┘
```

## Deployment Architecture

```
┌────────────────────────────────────────────────────────┐
│                    DOCKER DEPLOYMENT                   │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │ research-agent (main service)                │    │
│  │ • Interactive mode                           │    │
│  │ • Single query execution                     │    │
│  │ • Volume mounts: data/, results/             │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │ benchmark (profile: benchmark)               │    │
│  │ • Runs evaluation suite                      │    │
│  │ • Generates reports                          │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │ dataset-generator (profile: setup)           │    │
│  │ • Generates mock data                        │    │
│  │ • One-time setup                             │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │ Persistent Volumes                           │    │
│  │ • data/ (read-mostly)                        │    │
│  │ • results/ (read-write)                      │    │
│  │ • logs/ (write-only)                         │    │
│  └──────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────┘
```

## Key Design Patterns

1. **Chain of Responsibility**: Request flows through planner → executor → analyzer
2. **Strategy Pattern**: Tools implement common interface, selected at runtime
3. **Observer Pattern**: Context manager observes and records all actions
4. **Template Method**: Prompts follow structured templates
5. **Retry Pattern**: Exponential backoff for API failures
6. **Circuit Breaker**: Stop after repeated failures

## Performance Characteristics

- **Planning**: 2-5 seconds per plan
- **Tool Execution**: 0.1-1 second per tool
- **Analysis**: 2-4 seconds per iteration
- **Synthesis**: 3-6 seconds
- **Total**: 30-90 seconds for typical query
- **Token Usage**: 4,000-8,000 tokens per iteration

---

This architecture enables autonomous research with intelligent planning, execution, and refinement.

