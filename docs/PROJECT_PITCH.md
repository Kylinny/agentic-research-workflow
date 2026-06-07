# Project Pitch

## One-Line Version

I built a reproducible agentic research workflow that plans, executes tools, evaluates intermediate results, and synthesizes answers across social-discourse and research-paper datasets.

## Short Intro

This project started from a common AI engineering problem: lots of agent demos look good on stage, but they are fragile in local development. They often depend on external API keys, optional retrieval backends, and model behavior that is hard to validate repeatedly.

I turned that into a backend-focused project. The result is a multi-step research agent with:
- planning and tool orchestration
- offline deterministic execution
- retrieval fallback when embeddings are unavailable
- local benchmark and regression coverage

## Medium Intro

I wanted a side project that showed more than basic CRUD backend work, so I built an AI agent workflow that behaves like a small research runtime. A user submits a query, the agent creates a plan, executes retrieval and analysis tools, evaluates whether the results are good enough, and then synthesizes a final answer.

What makes the project stronger from an engineering perspective is that I also added:
- a deterministic offline client so the workflow can be demoed without live credentials
- a benchmark mode for repeated evaluation
- a graceful fallback from semantic retrieval to keyword-only retrieval
- regression tests for the offline path

That makes it much easier to explain as an AI systems project rather than a simple LLM wrapper.

## LinkedIn / Social Post

Built a side project to push past routine backend CRUD work: an agentic research workflow that plans tasks, runs retrieval tools, evaluates intermediate results, and synthesizes a final answer across X-style posts and research papers.

The part I’m happiest with is the engineering layer around the agent:
- deterministic offline mode for reproducible demos
- benchmark flow for local validation
- graceful fallback from semantic retrieval to keyword-only retrieval
- regression tests for the offline workflow

I wanted something that felt more like an AI backend / agent systems project than a chatbot demo, and this got much closer to that goal.

## Interview Answer

If someone asks “why did you build this?”, a strong answer is:

I wanted a project that demonstrated AI systems engineering rather than just API integration. So I built a research agent with a planner, executor, analyzer, and context manager, then focused on reproducibility: offline execution, fallback retrieval behavior, benchmark scripts, and regression tests. That gave me a project I could both demo reliably and discuss in terms of runtime tradeoffs and system design.
