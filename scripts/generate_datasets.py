"""
Generate high-quality mock datasets for X posts and research papers
"""
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict
import os

# Ensure data directory exists
os.makedirs("data", exist_ok=True)
os.makedirs("data/embeddings", exist_ok=True)

# Sample topics and themes
TOPICS = [
    "artificial intelligence", "machine learning", "climate change", "quantum computing",
    "biotechnology", "renewable energy", "space exploration", "neuroscience",
    "cybersecurity", "blockchain", "gene therapy", "autonomous vehicles",
    "AI safety", "fusion energy", "brain-computer interfaces", "synthetic biology"
]

SENTIMENTS = ["positive", "negative", "neutral", "mixed", "sarcastic"]

# Sample usernames for X data
USERNAMES = [
    "ai_researcher", "climate_activist", "tech_enthusiast", "dr_quantum",
    "bio_innovator", "space_explorer", "neuro_scientist", "crypto_expert",
    "security_pro", "future_tech", "science_daily", "research_hub",
    "innovation_lab", "tech_critic", "policy_maker", "industry_insider"
]

def generate_x_posts(num_posts: int = 500) -> List[Dict]:
    """Generate realistic X (Twitter) posts with threads, replies, and metadata"""
    posts = []
    post_id = 1
    
    # Generate main posts
    for _ in range(num_posts // 2):
        topic = random.choice(TOPICS)
        author = random.choice(USERNAMES)
        timestamp = datetime.now() - timedelta(days=random.randint(0, 365), 
                                               hours=random.randint(0, 23))
        
        # Create main post
        post = {
            "id": post_id,
            "author": author,
            "content": generate_post_content(topic),
            "timestamp": timestamp.isoformat(),
            "likes": random.randint(10, 10000),
            "retweets": random.randint(5, 5000),
            "replies_count": random.randint(0, 100),
            "topic": topic,
            "sentiment": random.choice(SENTIMENTS),
            "language": "en",
            "is_thread": random.random() < 0.3,
            "thread_id": None,
            "reply_to": None,
            "has_media": random.random() < 0.2,
            "verified_author": random.random() < 0.3
        }
        
        posts.append(post)
        current_id = post_id
        post_id += 1
        
        # Generate thread continuation if applicable
        if post["is_thread"]:
            thread_length = random.randint(2, 5)
            for i in range(thread_length - 1):
                thread_post = {
                    "id": post_id,
                    "author": author,
                    "content": generate_thread_continuation(topic, i + 2),
                    "timestamp": (timestamp + timedelta(minutes=random.randint(1, 30))).isoformat(),
                    "likes": random.randint(5, 1000),
                    "retweets": random.randint(2, 500),
                    "replies_count": random.randint(0, 20),
                    "topic": topic,
                    "sentiment": post["sentiment"],
                    "language": "en",
                    "is_thread": True,
                    "thread_id": current_id,
                    "reply_to": post_id - 1,
                    "has_media": False,
                    "verified_author": post["verified_author"]
                }
                posts.append(thread_post)
                post_id += 1
        
        # Generate replies
        num_replies = random.randint(0, 10)
        for _ in range(num_replies):
            reply_author = random.choice([u for u in USERNAMES if u != author])
            reply = {
                "id": post_id,
                "author": reply_author,
                "content": generate_reply_content(topic, post["sentiment"]),
                "timestamp": (timestamp + timedelta(minutes=random.randint(5, 1440))).isoformat(),
                "likes": random.randint(0, 500),
                "retweets": random.randint(0, 50),
                "replies_count": 0,
                "topic": topic,
                "sentiment": random.choice(SENTIMENTS),
                "language": "en",
                "is_thread": False,
                "thread_id": None,
                "reply_to": current_id,
                "has_media": False,
                "verified_author": random.random() < 0.2
            }
            posts.append(reply)
            post_id += 1
    
    return posts

def generate_post_content(topic: str) -> str:
    """Generate realistic post content"""
    templates = [
        f"Excited to share new findings on {topic}! This could revolutionize the field. Thread 🧵",
        f"Concerns about {topic} are overblown. Here's why the data doesn't support the hype.",
        f"Just published: comprehensive analysis of {topic}. Key insights in this thread 👇",
        f"Hot take: {topic} is the most underrated area of research right now.",
        f"Breaking: Major breakthrough in {topic} announced today. Implications are huge.",
        f"Why is nobody talking about {topic}? This deserves more attention.",
        f"Unpopular opinion: Current approaches to {topic} are fundamentally flawed.",
        f"Fascinating discussion on {topic} happening now. What are your thoughts?",
        f"New paper on {topic} just dropped. Initial reactions: 🤯",
        f"The ethics of {topic} need serious discussion. Here's what we should consider..."
    ]
    return random.choice(templates)

def generate_thread_continuation(topic: str, part: int) -> str:
    """Generate thread continuation content"""
    templates = [
        f"{part}/ First, let's look at the current state of {topic}. Recent data shows...",
        f"{part}/ The methodology here is crucial. Researchers used novel approaches to...",
        f"{part}/ Key finding: {topic} shows 3x improvement over previous methods.",
        f"{part}/ But there are limitations. Sample size concerns and...",
        f"{part}/ Looking ahead: What does this mean for the future of {topic}?",
        f"{part}/ Critics argue that {topic} research overlooks important factors.",
        f"{part}/ Comparison with alternative approaches shows interesting patterns."
    ]
    return random.choice(templates)

def generate_reply_content(topic: str, original_sentiment: str) -> str:
    """Generate realistic reply content with substance"""
    # Topic-specific responses with actual content
    topic_responses = {
        "artificial intelligence": [
            f"The potential of {topic} for healthcare is incredible - early diagnosis could save millions of lives.",
            f"But we need to address the bias issues in {topic} systems before widespread deployment.",
            f"Love how {topic} is accelerating drug discovery. Recent examples show 10x speedup.",
            f"Concerned about job displacement from {topic}. We need robust retraining programs.",
            f"The energy consumption of large {topic} models is unsustainable. Need more efficient architectures.",
        ],
        "machine learning": [
            f"Transfer learning has been a game-changer for {topic} applications with limited data.",
            f"The reproducibility crisis in {topic} research needs urgent attention.",
            f"Interesting how {topic} is now being applied to climate modeling with promising results.",
            f"Model interpretability remains the biggest challenge for {topic} in critical applications.",
            f"The democratization of {topic} tools has been amazing - anyone can build now.",
        ],
        "climate change": [
            f"The latest IPCC report on {topic} is sobering. We're running out of time.",
            f"Tech solutions for {topic} are important but we can't ignore systemic policy changes.",
            f"Seeing more extreme weather events - {topic} impacts are already here.",
            f"The economic cost of inaction on {topic} far exceeds mitigation costs.",
            f"Carbon capture technology is promising but needs massive scale-up to combat {topic}.",
        ],
        "quantum computing": [
            f"IBM's recent advances in {topic} error correction are groundbreaking.",
            f"Still skeptical about {topic} timelines - we're decades from practical applications.",
            f"The cryptography implications of {topic} are both exciting and concerning.",
            f"Drug discovery could be revolutionized by {topic} - molecular simulation at scale.",
            f"Investment in {topic} startups has exploded - bubble or justified?",
        ],
        "cybersecurity": [
            f"The supply chain attacks we're seeing highlight critical {topic} vulnerabilities.",
            f"Zero-trust architecture is becoming essential for modern {topic}.",
            f"AI-powered {topic} threats are evolving faster than our defenses.",
            f"Ransomware is now a nation-state level problem beyond traditional {topic}.",
            f"The talent shortage in {topic} is getting worse - we need more training programs.",
        ]
    }
    
    # Default substantive templates that work for any topic
    agree_templates = [
        f"Completely agree! {topic.title()} is transforming the field in unexpected ways.",
        f"Great analysis! Would add that recent developments in {topic} support this view.",
        f"Yes! The scalability of {topic} approaches has improved dramatically.",
        f"Brilliant thread. The economic implications of {topic} are massive.",
        f"This aligns with what we're seeing in {topic} deployments across industries.",
    ]
    
    disagree_templates = [
        f"Have to disagree. Recent studies on {topic} show different outcomes.",
        f"This overlooks regulatory challenges that {topic} implementations face.",
        f"The timeline seems optimistic given current {topic} limitations.",
        f"Respectfully, this interpretation of {topic} misses key ethical considerations.",
        f"Data quality issues in {topic} research make these claims premature.",
    ]
    
    neutral_templates = [
        f"Interesting perspective on {topic}. What about the scalability challenges?",
        f"Can you elaborate on how this applies to {topic} in developing markets?",
        f"The long-term sustainability of {topic} approaches needs more study.",
        f"Would love to see comparative analysis with alternative {topic} methods.",
        f"How does this {topic} approach handle edge cases and failure modes?",
    ]
    
    # Use topic-specific if available, otherwise use enhanced generic
    if topic in topic_responses:
        all_responses = topic_responses[topic] + agree_templates + disagree_templates + neutral_templates
        return random.choice(all_responses)
    else:
        if original_sentiment in ["positive", "neutral"]:
            if random.random() < 0.7:
                return random.choice(agree_templates)
            else:
                return random.choice(disagree_templates)
        else:
            if random.random() < 0.5:
                return random.choice(disagree_templates)
            else:
                return random.choice(neutral_templates)

def generate_research_papers(num_papers: int = 200) -> List[Dict]:
    """Generate realistic research paper metadata and abstracts"""
    papers = []
    
    for i in range(num_papers):
        topic = random.choice(TOPICS)
        year = random.randint(2015, 2025)
        
        paper = {
            "id": f"paper_{i+1}",
            "title": generate_paper_title(topic),
            "authors": [random.choice(USERNAMES).replace("_", " ").title() 
                       for _ in range(random.randint(2, 6))],
            "year": year,
            "venue": random.choice([
                "Nature", "Science", "Cell", "PNAS", "NeurIPS", "ICML", 
                "ICLR", "CVPR", "ACL", "EMNLP", "IJCAI", "AAAI"
            ]),
            "abstract": generate_abstract(topic),
            "keywords": generate_keywords(topic),
            "citations_count": random.randint(0, 1000),
            "doi": f"10.1000/journal.{year}.{i+1:04d}",
            "arxiv_id": f"{year-2000}{random.randint(10,12)}.{random.randint(1000,9999)}",
            "field": categorize_topic(topic),
            "methodology": random.choice([
                "Experimental", "Theoretical", "Computational", 
                "Survey", "Meta-analysis", "Case study"
            ]),
            "open_access": random.random() < 0.5,
            "citations": []  # Will be populated in post-processing
        }
        
        papers.append(paper)
    
    # Add citation relationships
    for paper in papers:
        num_citations = random.randint(0, 15)
        cited_papers = random.sample([p["id"] for p in papers if p != paper], 
                                     min(num_citations, len(papers) - 1))
        paper["citations"] = cited_papers
    
    return papers

def generate_paper_title(topic: str) -> str:
    """Generate realistic paper title"""
    templates = [
        f"Advances in {topic}: A Comprehensive Survey",
        f"Towards Efficient {topic} via Novel Architectures",
        f"Understanding {topic}: Theory and Practice",
        f"{topic} at Scale: Challenges and Solutions",
        f"Rethinking {topic}: A New Framework",
        f"Deep Learning for {topic}: Methods and Applications",
        f"Interpretable {topic} with Explainable AI",
        f"Robust {topic} Under Distribution Shift",
        f"Federated Approaches to {topic}",
        f"Cross-Modal {topic} with Transformers"
    ]
    return random.choice(templates)

def generate_abstract(topic: str) -> str:
    """Generate realistic abstract"""
    return f"""Recent advances in {topic} have shown promising results, but significant 
challenges remain. In this work, we propose a novel approach that addresses key limitations 
of existing methods. Our method combines theoretical insights with empirical validation, 
achieving state-of-the-art performance on multiple benchmarks. We demonstrate that our 
approach scales effectively to real-world scenarios while maintaining interpretability. 
Extensive experiments across diverse datasets show improvements of 15-30% over previous 
best methods. We also provide theoretical analysis showing convergence guarantees under 
mild assumptions. Our findings suggest that {topic} research could benefit from 
cross-disciplinary approaches, and we identify several promising directions for future work. 
Code and data are made available to facilitate reproducibility."""

def generate_keywords(topic: str) -> List[str]:
    """Generate relevant keywords"""
    base_keywords = topic.split()
    additional = random.sample([
        "machine learning", "deep learning", "neural networks", "optimization",
        "scalability", "robustness", "interpretability", "efficiency",
        "real-world applications", "theoretical analysis", "benchmark",
        "state-of-the-art", "novel architecture", "transfer learning"
    ], k=random.randint(3, 7))
    return base_keywords + additional

def categorize_topic(topic: str) -> str:
    """Categorize topic into broader field"""
    categories = {
        "computer_science": ["artificial intelligence", "machine learning", "quantum computing", 
                            "cybersecurity", "blockchain", "autonomous vehicles"],
        "biology": ["biotechnology", "gene therapy", "neuroscience", "synthetic biology"],
        "environmental": ["climate change", "renewable energy"],
        "physics": ["quantum computing", "fusion energy", "space exploration"],
        "interdisciplinary": ["brain-computer interfaces", "AI safety"]
    }
    
    for category, topics in categories.items():
        if topic in topics:
            return category
    return "other"

def main():
    """Generate and save datasets"""
    print("Generating X posts dataset...")
    x_posts = generate_x_posts(num_posts=500)
    
    with open("data/x_posts.json", "w") as f:
        json.dump(x_posts, f, indent=2)
    print(f"✓ Generated {len(x_posts)} X posts")
    
    print("\nGenerating research papers dataset...")
    papers = generate_research_papers(num_papers=200)
    
    with open("data/research_papers.json", "w") as f:
        json.dump(papers, f, indent=2)
    print(f"✓ Generated {len(papers)} research papers")
    
    # Generate statistics
    stats = {
        "x_posts": {
            "total": len(x_posts),
            "threads": sum(1 for p in x_posts if p["is_thread"]),
            "replies": sum(1 for p in x_posts if p["reply_to"] is not None),
            "topics": len(set(p["topic"] for p in x_posts)),
            "date_range": {
                "earliest": min(p["timestamp"] for p in x_posts),
                "latest": max(p["timestamp"] for p in x_posts)
            }
        },
        "research_papers": {
            "total": len(papers),
            "year_range": f"{min(p['year'] for p in papers)}-{max(p['year'] for p in papers)}",
            "venues": len(set(p["venue"] for p in papers)),
            "fields": len(set(p["field"] for p in papers))
        }
    }
    
    with open("data/dataset_stats.json", "w") as f:
        json.dump(stats, f, indent=2)
    
    print("\n" + "="*50)
    print("Dataset Generation Complete!")
    print("="*50)
    print(f"X Posts: {stats['x_posts']['total']}")
    print(f"  - Threads: {stats['x_posts']['threads']}")
    print(f"  - Replies: {stats['x_posts']['replies']}")
    print(f"  - Topics: {stats['x_posts']['topics']}")
    print(f"\nResearch Papers: {stats['research_papers']['total']}")
    print(f"  - Years: {stats['research_papers']['year_range']}")
    print(f"  - Venues: {stats['research_papers']['venues']}")
    print(f"  - Fields: {stats['research_papers']['fields']}")
    print("\nFiles saved to data/ directory")

if __name__ == "__main__":
    main()

