# Sample Output

Command used:

```bash
python main.py --offline --query "How does X discourse on biotechnology compare to academic research?"
```

Representative output:

```text
RESEARCH RESULTS

Query: How does X discourse on biotechnology compare to academic research?

Status: SUCCESS

Executive Summary
This offline workflow aligned local social-discourse retrieval with academic paper search
to produce a reproducible research brief without requiring live model credentials.

Key Findings
- Public discourse emphasized commercialization, risk perception, and hype cycles.
- Paper retrieval surfaced methodology-heavy discussions and citation-linked evidence.
- The workflow completed in a single iteration with keyword-only retrieval fallback.

Limitations
- This answer was produced in offline heuristic mode using local datasets and deterministic planning.
- Final judgments should be validated with a live model and broader sources.

Confidence
Medium confidence for demo and workflow validation; lower confidence for real-world research conclusions.

STATISTICS
Model: grok-4-latest
Iterations: 1
Tasks: 2/2 successful
Replans: 0
Quality Metrics:
  Completeness: 1.00
  Coherence: 0.60
  Evidence Support: 0.33
  Overall Score: 0.68
Token Usage:
  Prompt: 615
  Completion: 105
  Total: 720
```
