# Demo Guide & Video Instructions

## Creating Your 4-5 Minute Demo Video

### Video Structure

#### Part 1: Introduction (30 seconds)
- Introduce the project: "Agentic Research Workflow with Grok"
- Brief overview of capabilities
- Show architecture diagram from README

#### Part 2: System Architecture (1 minute)
- Walk through components:
  - Grok integration layer
  - Agent core (planner, executor, analyzer)
  - Tools (X search, paper search, hybrid retrieval, etc.)
  - Context manager
- Show key code files briefly

#### Part 3: Live Demo - Simple Query (1.5 minutes)
```bash
# Start with a simple query to show basic functionality
python main.py --query "What are users saying about climate change on X?"
```

**What to highlight**:
- ✓ Agent creates initial plan
- ✓ Executes search and sentiment analysis
- ✓ Analyzes results
- ✓ Synthesizes coherent answer with evidence
- ✓ Show final output and metrics

#### Part 4: Live Demo - Complex Query (1.5 minutes)
```bash
# Show a complex cross-domain query
python main.py --query "How does public discourse on X about AI safety align with academic research findings? Identify key differences."
```

**What to highlight**:
- ✓ Plan decomposition (multiple sub-tasks)
- ✓ Tool selection and execution
- ✓ Replanning if ambiguity detected
- ✓ Cross-domain synthesis (X + research papers)
- ✓ Quality metrics and completion stats

#### Part 5: Key Features & Decision Explanations (1 minute)
- **Iterative Loop**: Show execution trace
- **Replanning**: Explain when and why it happens
- **Context Management**: How memory is maintained
- **Tool Selection**: How agent chooses appropriate tools
- **Quality Assessment**: How results are evaluated

### Demo Scenarios

#### Scenario 1: Sentiment Analysis
```bash
python main.py --query "Analyze sentiment trends about artificial intelligence on X. Who are the key influencers?"
```

**Expected flow**:
1. Plan: Search X posts → Sentiment analysis → Influencer identification
2. Execute: XSearchTool finds relevant posts
3. Execute: SentimentAnalysisTool analyzes sentiment
4. Execute: Find top influencers by engagement
5. Synthesize: Summary of sentiment trends + influencer list

#### Scenario 2: Research Paper Analysis
```bash
python main.py --query "What are the most influential papers in quantum computing based on citation networks?"
```

**Expected flow**:
1. Plan: Paper search → Citation tracking → Impact analysis
2. Execute: PaperSearchTool finds quantum computing papers
3. Execute: CitationTrackerTool builds citation network
4. Execute: Calculate impact metrics
5. Synthesize: Ranked list with justification

#### Scenario 3: Cross-Domain Comparison
```bash
python main.py --query "Compare methodologies in machine learning papers from 2020 vs 2025"
```

**Expected flow**:
1. Plan: Search papers by year → Extract methodologies → Compare
2. Execute: PaperSearchTool with year filters
3. Execute: Methodology extraction
4. Analyze: Identify patterns and changes
5. Synthesize: Evolution summary with examples

#### Scenario 4: Thread Analysis
```bash
python main.py --query "Find controversial discussions about biotechnology on X and analyze different viewpoints"
```

**Expected flow**:
1. Plan: Search threads → Sentiment analysis → Viewpoint extraction
2. Execute: XSearchTool finds threads
3. Execute: Thread analysis with sentiment
4. Execute: Identify polarization
5. Synthesize: Controversy summary with opposing views

### Recording Tips

#### Screen Recording Setup
```bash
# Use QuickTime (Mac) or OBS Studio
# Resolution: 1920x1080
# Frame rate: 30fps
# Audio: Enable microphone for narration
```

#### Terminal Setup for Recording
```bash
# Use a clean terminal with good contrast
# Increase font size for visibility
export PS1="\[\e[32m\]\u@\h \[\e[34m\]\w\[\e[0m\]\$ "

# Clear screen before each command
clear

# Use --verbose flag for visual progress
python main.py --verbose --query "..."
```

#### What to Show on Screen
- Terminal with command execution
- Real-time agent progress (colored output)
- Key decision points (planning, replanning)
- Final results and metrics
- Briefly show relevant code (optional)

### Demo Script Example

```
"Hello! Today I'll demonstrate an autonomous research agent built with Grok.

[Show architecture]
The system uses Grok as the central reasoner, coordinating multiple specialized 
tools to answer complex research questions.

[Run simple query]
Let's start with a simple query about AI safety discussions on X...
Notice how the agent:
1. Creates a plan automatically
2. Executes searches and sentiment analysis
3. Synthesizes a coherent answer with citations

[Run complex query]
Now for something more challenging - a cross-domain analysis...
Here the agent:
1. Breaks down the query into sub-tasks
2. Searches both X posts and research papers
3. Identifies gaps and differences
4. Synthesizes comprehensive findings

[Show decision explanation]
Key features that make this work:
- Adaptive replanning when encountering ambiguity
- Context management across iterations
- Quality assessment at each step
- Tool selection based on task requirements

[Show results]
The agent completed this in 3 iterations, executing 8 tasks with 1 replan.
Quality score: 0.85. All with relevant citations.

[Conclusion]
This demonstrates true agentic behavior - autonomous planning, execution, 
and refinement to answer complex research questions. Thank you!"
```

### Post-Recording Checklist

- [ ] Video length: 4-5 minutes
- [ ] Audio clear and audible
- [ ] Terminal text readable
- [ ] Shows live execution (not screenshots)
- [ ] Demonstrates replanning or complex decision
- [ ] Explains key architectural decisions
- [ ] Shows final results and metrics
- [ ] Professional presentation

### Quick Demo Commands

```bash
# Demo 1: Basic functionality
python main.py --query "What are the latest trends in renewable energy research?"

# Demo 2: Cross-domain
python main.py --query "How does X sentiment about quantum computing compare to academic research focus?"

# Demo 3: Complex analysis
python main.py --query "Build a citation network for influential AI safety papers and identify research gaps"

# Demo 4: Show evaluation
python evaluation/run_benchmark.py --max-queries 3

# Demo 5: Model comparison (if time allows)
python evaluation/compare_models.py --max-queries 3
```

### Backup Plan

If live demo fails during recording:

```bash
# Have pre-generated results ready
ls results/

# Show a successful result
cat results/result_0.json | jq .

# Explain what would have happened
# Show execution trace
cat results/result_0.json | jq '.execution_trace'
```

### Video Editing (Optional)

If you edit the video:
- Speed up slow parts (waiting for API responses)
- Add annotations for key concepts
- Highlight important output in terminal
- Add title slide and conclusion slide

### Submission

Export video as:
- Format: MP4 (H.264)
- Resolution: 1920x1080 or 1280x720
- File size: Under 100MB (compress if needed)

---

**Pro Tips**:
1. Practice the demo 2-3 times before recording
2. Have queries ready in a text file for copy-paste
3. Clear terminal between demos
4. Speak clearly and not too fast
5. Show enthusiasm - this is cool tech!
6. If something goes wrong, explain what you expected
7. Focus on the agent's decision-making, not just results

Good luck with your demo! 🎥

