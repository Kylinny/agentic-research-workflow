# Resume Notes

## Project Positioning

This project is strongest when presented as an **AI backend / agent systems** project rather than a generic chatbot demo.

Recommended framing:
- multi-step agent workflow
- tool orchestration across heterogeneous data sources
- reproducible offline execution for local validation
- benchmarkable research pipeline with graceful degradation

## Suggested Resume Bullets

### English

- Built an agentic research workflow that plans, executes tools, analyzes intermediate results, and synthesizes final answers across mock social-discourse and research-paper datasets.
- Added a deterministic offline execution mode and local benchmark pipeline so the system can be reproduced and demoed without live model credentials.
- Improved retrieval robustness by introducing graceful degradation from semantic retrieval to keyword-only retrieval when embedding backends are unavailable.
- Added offline regression tests covering planning, retrieval fallback, end-to-end execution, and benchmark output generation.

### Chinese

- 设计并实现一个 agentic research workflow，支持 query planning、tool execution、intermediate analysis 和 final synthesis 的多步推理流程。
- 为系统增加 deterministic 离线执行模式与本地 benchmark 流程，使项目在没有线上模型凭证时也可复现和演示。
- 重构 hybrid retrieval，加入 semantic retrieval 到 keyword-only retrieval 的 graceful degradation 机制，提升系统健壮性。
- 补充离线回归测试，覆盖规划、检索降级、端到端执行与 benchmark 结果生成。

## Interview Story

Use this structure when talking about the project:

1. Problem
AI agents are often impressive in demos but brittle in local development because they depend on API keys, unstable model behavior, and optional retrieval backends.

2. What I built
I built a research-oriented agent workflow with planning, tool execution, result analysis, and synthesis across multiple local datasets.

3. Engineering decisions
- Added offline deterministic mode for reproducibility
- Added fallback retrieval path to avoid hard dependency on embeddings
- Added local regression coverage so changes can be validated quickly

4. Outcome
The project became easier to demo, benchmark, and iterate on as an engineering system rather than just a prompt prototype.
