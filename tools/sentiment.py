"""
Sentiment analysis tool for X posts and research content
"""
from typing import List, Dict
import re

class SentimentAnalysisTool:
    """Tool for analyzing sentiment in text data"""
    
    def __init__(self):
        # Simple rule-based sentiment analysis
        # In production, would use a model like VADER or transformer
        self.positive_words = {
            'excellent', 'great', 'amazing', 'breakthrough', 'innovative',
            'revolutionary', 'excited', 'promising', 'impressive', 'outstanding',
            'significant', 'important', 'successful', 'effective', 'powerful',
            'brilliant', 'fascinating', 'wonderful', 'fantastic', 'love'
        }
        
        self.negative_words = {
            'terrible', 'bad', 'awful', 'disappointing', 'failed', 'failure',
            'flawed', 'problematic', 'concerning', 'worried', 'issue', 'problem',
            'limitation', 'weak', 'poor', 'ineffective', 'incorrect', 'wrong',
            'misleading', 'dangerous', 'hate', 'worst'
        }
        
        self.sarcasm_indicators = {
            'sure', 'totally', 'obviously', 'clearly', 'definitely',
            'yeah right', 'of course', 'oh wow'
        }
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze sentiment of a single text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with sentiment label, score, and confidence
        """
        text_lower = text.lower()
        words = set(re.findall(r'\b\w+\b', text_lower))
        
        # Count positive and negative words
        pos_count = len(words & self.positive_words)
        neg_count = len(words & self.negative_words)
        
        # Check for sarcasm indicators
        has_sarcasm = any(indicator in text_lower for indicator in self.sarcasm_indicators)
        
        # Calculate sentiment score (-1 to 1)
        total = pos_count + neg_count
        if total == 0:
            sentiment_score = 0.0
            label = "neutral"
        else:
            sentiment_score = (pos_count - neg_count) / total
            
            if sentiment_score > 0.3:
                label = "positive"
            elif sentiment_score < -0.3:
                label = "negative"
            else:
                label = "neutral"
        
        # Adjust for sarcasm
        if has_sarcasm and label == "positive":
            label = "sarcastic"
            sentiment_score = -abs(sentiment_score) * 0.5
        
        # Calculate confidence based on word count
        confidence = min(total / 5.0, 1.0) * 0.7  # Rule-based has lower confidence
        
        return {
            "label": label,
            "score": sentiment_score,
            "confidence": confidence,
            "positive_words": pos_count,
            "negative_words": neg_count,
            "has_sarcasm": has_sarcasm
        }
    
    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """Analyze sentiment for multiple texts"""
        return [self.analyze(text) for text in texts]
    
    def analyze_thread(self, posts: List[Dict]) -> Dict:
        """
        Analyze sentiment evolution in a thread
        
        Args:
            posts: List of posts in chronological order
            
        Returns:
            Dict with thread-level sentiment analysis
        """
        if not posts:
            return {"error": "No posts provided"}
        
        sentiments = []
        for post in posts:
            # Handle both "text" and "content" fields
            content = post.get("text", post.get("content", ""))
            if not content:
                continue  # Skip empty posts
            sentiment = self.analyze(content)
            sentiment["post_id"] = post.get("id", post.get("post_id"))
            sentiment["timestamp"] = post.get("timestamp", post.get("created_at"))
            sentiments.append(sentiment)
        
        if not sentiments:
            return {"error": "No valid posts to analyze"}
        
        # Calculate overall thread sentiment
        avg_score = sum(s["score"] for s in sentiments) / len(sentiments)
        
        # Determine if sentiment shifts
        scores = [s["score"] for s in sentiments]
        shifts = []
        for i in range(1, len(scores)):
            if abs(scores[i] - scores[i-1]) > 0.5:
                shifts.append({
                    "from_post": sentiments[i-1]["post_id"],
                    "to_post": sentiments[i]["post_id"],
                    "magnitude": scores[i] - scores[i-1]
                })
        
        return {
            "thread_id": posts[0].get("thread_id") or posts[0].get("id"),
            "num_posts": len(posts),
            "overall_sentiment": self._score_to_label(avg_score),
            "average_score": avg_score,
            "sentiment_by_post": sentiments,
            "shifts": shifts,
            "shift_count": len(shifts)
        }
    
    def analyze_conversation(self, main_post: Dict, replies: List[Dict]) -> Dict:
        """
        Analyze sentiment in a conversation (post + replies)
        
        Args:
            main_post: The original post
            replies: List of reply posts
            
        Returns:
            Dict with conversation sentiment analysis
        """
        # Handle both "text" and "content" fields
        main_text = main_post.get("text", main_post.get("content", ""))
        main_sentiment = self.analyze(main_text)
        reply_sentiments = [
            self.analyze(r.get("text", r.get("content", ""))) 
            for r in replies
        ]
        
        # Classify replies as agreeing or disagreeing
        agreement = []
        disagreement = []
        neutral_replies = []
        
        for reply, sentiment in zip(replies, reply_sentiments):
            score_diff = abs(sentiment["score"] - main_sentiment["score"])
            
            if score_diff < 0.3:
                agreement.append(reply)
            elif score_diff > 0.6:
                disagreement.append(reply)
            else:
                neutral_replies.append(reply)
        
        return {
            "main_post": {
                "id": main_post.get("id"),
                "sentiment": main_sentiment
            },
            "reply_count": len(replies),
            "agreement_count": len(agreement),
            "disagreement_count": len(disagreement),
            "neutral_count": len(neutral_replies),
            "agreement_ratio": len(agreement) / len(replies) if replies else 0,
            "polarization_score": len(disagreement) / len(replies) if replies else 0,
            "reply_sentiments": reply_sentiments
        }
    
    def aggregate_sentiment(self, posts: List[Dict], group_by: str = None) -> Dict:
        """
        Aggregate sentiment across multiple posts
        
        Args:
            posts: List of posts to analyze
            group_by: Optional field to group by (e.g., 'topic', 'author')
            
        Returns:
            Dict with aggregated sentiment statistics
        """
        if not posts:
            return {"error": "No posts provided"}
        
        # Handle both "text" and "content" fields, filter out empty
        texts = [
            p.get("text", p.get("content", "")) 
            for p in posts 
            if p.get("text") or p.get("content")
        ]
        
        if not texts:
            return {"error": "No valid text content in posts"}
        
        sentiments = self.analyze_batch(texts)
        
        # Overall statistics
        stats = {
            "total_posts": len(posts),
            "sentiment_distribution": {
                "positive": sum(1 for s in sentiments if s["label"] == "positive"),
                "negative": sum(1 for s in sentiments if s["label"] == "negative"),
                "neutral": sum(1 for s in sentiments if s["label"] == "neutral"),
                "sarcastic": sum(1 for s in sentiments if s["label"] == "sarcastic")
            },
            "average_score": sum(s["score"] for s in sentiments) / len(sentiments),
            "average_confidence": sum(s["confidence"] for s in sentiments) / len(sentiments)
        }
        
        # Group by if specified
        if group_by:
            groups = {}
            for post, sentiment in zip(posts, sentiments):
                key = post.get(group_by, "unknown")
                if key not in groups:
                    groups[key] = []
                groups[key].append(sentiment)
            
            stats["by_" + group_by] = {}
            for key, group_sentiments in groups.items():
                stats["by_" + group_by][key] = {
                    "count": len(group_sentiments),
                    "average_score": sum(s["score"] for s in group_sentiments) / len(group_sentiments),
                    "distribution": {
                        label: sum(1 for s in group_sentiments if s["label"] == label)
                        for label in ["positive", "negative", "neutral", "sarcastic"]
                    }
                }
        
        return stats
    
    def _score_to_label(self, score: float) -> str:
        """Convert numerical score to label"""
        if score > 0.3:
            return "positive"
        elif score < -0.3:
            return "negative"
        else:
            return "neutral"

