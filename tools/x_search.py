"""
X (Twitter) data search and analysis tool
"""
import json
from typing import List, Dict, Optional
from datetime import datetime
import os

class XSearchTool:
    """Tool for searching and analyzing X posts and threads"""
    
    def __init__(self, data_path: str = "data/x_posts.json"):
        self.data_path = data_path
        self.posts = self._load_posts()
    
    def _load_posts(self) -> List[Dict]:
        """Load X posts from JSON file"""
        if not os.path.exists(self.data_path):
            return []
        
        with open(self.data_path, 'r') as f:
            return json.load(f)
    
    def search(
        self,
        query: str,
        filters: Optional[Dict] = None,
        limit: int = 20
    ) -> List[Dict]:
        """
        Search X posts by content and filters
        
        Args:
            query: Search query string
            filters: Optional filters (author, topic, sentiment, date_range, etc.)
            limit: Maximum number of results
            
        Returns:
            List of matching posts
        """
        results = []
        query_lower = query.lower()
        
        for post in self.posts:
            # Content matching
            if query_lower in post["content"].lower():
                # Apply filters
                if filters and not self._matches_filters(post, filters):
                    continue
                
                results.append(post)
                
                if len(results) >= limit:
                    break
        
        return results
    
    def get_thread(self, thread_id: int) -> List[Dict]:
        """Get all posts in a thread"""
        thread_posts = []
        
        # Get the main post
        main_post = next((p for p in self.posts if p["id"] == thread_id), None)
        if main_post:
            thread_posts.append(main_post)
        
        # Get thread continuations
        continuations = [p for p in self.posts 
                        if p.get("thread_id") == thread_id]
        thread_posts.extend(sorted(continuations, key=lambda x: x["id"]))
        
        return thread_posts
    
    def get_replies(self, post_id: int) -> List[Dict]:
        """Get all replies to a post"""
        return [p for p in self.posts if p.get("reply_to") == post_id]
    
    def get_conversation(self, post_id: int) -> Dict:
        """Get full conversation tree for a post"""
        main_post = next((p for p in self.posts if p["id"] == post_id), None)
        
        if not main_post:
            return {"error": "Post not found"}
        
        # Get thread if applicable
        if main_post.get("is_thread"):
            thread = self.get_thread(post_id)
        elif main_post.get("thread_id"):
            thread = self.get_thread(main_post["thread_id"])
        else:
            thread = [main_post]
        
        # Get replies to each post in thread
        conversation = {
            "main_post": main_post,
            "thread": thread,
            "replies": {}
        }
        
        for post in thread:
            replies = self.get_replies(post["id"])
            conversation["replies"][post["id"]] = replies
        
        return conversation
    
    def analyze_sentiment_trends(
        self,
        topic: str,
        time_window_days: int = 30
    ) -> Dict:
        """Analyze sentiment trends for a topic over time"""
        # Filter posts by topic
        topic_posts = [p for p in self.posts if p.get("topic") == topic]
        
        # Sort by timestamp
        topic_posts.sort(key=lambda x: x["timestamp"])
        
        # Group by sentiment
        sentiment_counts = {}
        for post in topic_posts:
            sentiment = post.get("sentiment", "neutral")
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        
        # Calculate engagement metrics
        total_likes = sum(p.get("likes", 0) for p in topic_posts)
        total_retweets = sum(p.get("retweets", 0) for p in topic_posts)
        
        return {
            "topic": topic,
            "total_posts": len(topic_posts),
            "sentiment_distribution": sentiment_counts,
            "engagement": {
                "total_likes": total_likes,
                "total_retweets": total_retweets,
                "avg_likes": total_likes / len(topic_posts) if topic_posts else 0,
                "avg_retweets": total_retweets / len(topic_posts) if topic_posts else 0
            },
            "date_range": {
                "earliest": topic_posts[0]["timestamp"] if topic_posts else None,
                "latest": topic_posts[-1]["timestamp"] if topic_posts else None
            }
        }
    
    def find_influencers(self, topic: str, top_n: int = 10) -> List[Dict]:
        """Find top influencers for a topic based on engagement"""
        # Filter posts by topic
        topic_posts = [p for p in self.posts if p.get("topic") == topic]
        
        # Aggregate by author
        author_stats = {}
        for post in topic_posts:
            author = post["author"]
            if author not in author_stats:
                author_stats[author] = {
                    "author": author,
                    "post_count": 0,
                    "total_likes": 0,
                    "total_retweets": 0,
                    "verified": post.get("verified_author", False)
                }
            
            author_stats[author]["post_count"] += 1
            author_stats[author]["total_likes"] += post.get("likes", 0)
            author_stats[author]["total_retweets"] += post.get("retweets", 0)
        
        # Calculate influence score
        for author in author_stats.values():
            author["influence_score"] = (
                author["total_likes"] * 0.5 +
                author["total_retweets"] * 1.5 +
                author["post_count"] * 10 +
                (100 if author["verified"] else 0)
            )
        
        # Sort by influence score
        influencers = sorted(
            author_stats.values(),
            key=lambda x: x["influence_score"],
            reverse=True
        )
        
        return influencers[:top_n]
    
    def _matches_filters(self, post: Dict, filters: Dict) -> bool:
        """Check if post matches all filters"""
        for key, value in filters.items():
            if key == "date_after":
                if post["timestamp"] < value:
                    return False
            elif key == "date_before":
                if post["timestamp"] > value:
                    return False
            elif key == "min_likes":
                if post.get("likes", 0) < value:
                    return False
            elif key == "verified_only":
                if value and not post.get("verified_author", False):
                    return False
            elif isinstance(value, list):
                if post.get(key) not in value:
                    return False
            else:
                if post.get(key) != value:
                    return False
        
        return True

