"""
Hybrid retrieval combining semantic and keyword search
"""
import json
import numpy as np
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import os

class HybridRetrievalTool:
    """Hybrid search combining semantic embeddings and keyword matching"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.embeddings_cache = {}
        self.documents = {}
        
    def load_documents(self, doc_type: str) -> List[Dict]:
        """Load documents from JSON file"""
        file_map = {
            "x_posts": "x_posts.json",
            "papers": "research_papers.json"
        }
        
        file_path = os.path.join(self.data_dir, file_map.get(doc_type, f"{doc_type}.json"))
        
        if not os.path.exists(file_path):
            return []
        
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def get_embeddings(self, texts: List[str], cache_key: str) -> np.ndarray:
        """Get or compute embeddings for texts"""
        if cache_key in self.embeddings_cache:
            return self.embeddings_cache[cache_key]
        
        embeddings = self.encoder.encode(texts, convert_to_numpy=True)
        self.embeddings_cache[cache_key] = embeddings
        return embeddings
    
    def keyword_score(self, query: str, text: str) -> float:
        """Compute keyword matching score"""
        query_terms = set(query.lower().split())
        text_terms = set(text.lower().split())
        
        if not query_terms:
            return 0.0
        
        # Exact match bonus
        exact_match = 1.0 if query.lower() in text.lower() else 0.0
        
        # Term overlap
        overlap = len(query_terms & text_terms) / len(query_terms)
        
        return 0.7 * overlap + 0.3 * exact_match
    
    def semantic_score(self, query_embedding: np.ndarray, doc_embedding: np.ndarray) -> float:
        """Compute cosine similarity"""
        return np.dot(query_embedding, doc_embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
        )
    
    def search(
        self,
        query: str,
        doc_type: str = "x_posts",
        top_k: int = 10,
        semantic_weight: float = 0.6,
        keyword_weight: float = 0.4,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Perform hybrid search
        
        Args:
            query: Search query
            doc_type: Type of documents to search ('x_posts' or 'papers')
            top_k: Number of results to return
            semantic_weight: Weight for semantic similarity (0-1)
            keyword_weight: Weight for keyword matching (0-1)
            filters: Optional filters (e.g., {'topic': 'AI', 'year': 2023})
            
        Returns:
            List of top-k documents with scores
        """
        # Load documents
        docs = self.load_documents(doc_type)
        
        if not docs:
            return []
        
        # Apply filters
        if filters:
            docs = self._apply_filters(docs, filters)
        
        # Prepare texts for embedding
        if doc_type == "x_posts":
            texts = [d.get("content", "") for d in docs]
        else:  # papers
            texts = [d.get("title", "") + " " + d.get("abstract", "") for d in docs]
        
        # Compute query embedding
        query_embedding = self.encoder.encode([query], convert_to_numpy=True)[0]
        
        # Get document embeddings
        doc_embeddings = self.get_embeddings(texts, f"{doc_type}_embeddings")
        
        # Compute scores
        results = []
        for idx, (doc, text, doc_emb) in enumerate(zip(docs, texts, doc_embeddings)):
            sem_score = self.semantic_score(query_embedding, doc_emb)
            kw_score = self.keyword_score(query, text)
            
            combined_score = (semantic_weight * sem_score + 
                            keyword_weight * kw_score)
            
            result = {
                **doc,
                "relevance_score": float(combined_score),
                "semantic_score": float(sem_score),
                "keyword_score": float(kw_score),
                "matched_text": text[:200] + "..." if len(text) > 200 else text
            }
            results.append(result)
        
        # Sort by combined score
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return results[:top_k]
    
    def _apply_filters(self, docs: List[Dict], filters: Dict) -> List[Dict]:
        """Apply filters to documents"""
        filtered = docs
        
        for key, value in filters.items():
            if isinstance(value, list):
                filtered = [d for d in filtered if d.get(key) in value]
            else:
                filtered = [d for d in filtered if d.get(key) == value]
        
        return filtered
    
    def multi_hop_search(
        self,
        initial_query: str,
        doc_type: str = "x_posts",
        hops: int = 2,
        top_k_per_hop: int = 5
    ) -> Dict:
        """
        Perform multi-hop retrieval for complex queries
        
        Args:
            initial_query: Starting query
            doc_type: Document type
            hops: Number of retrieval hops
            top_k_per_hop: Documents per hop
            
        Returns:
            Dict with results from each hop and synthesis
        """
        results_by_hop = []
        current_context = initial_query
        
        for hop in range(hops):
            # Search with current context
            hop_results = self.search(
                query=current_context,
                doc_type=doc_type,
                top_k=top_k_per_hop
            )
            
            results_by_hop.append({
                "hop": hop + 1,
                "query": current_context,
                "results": hop_results
            })
            
            # Update context for next hop
            if hop_results and hop < hops - 1:
                # Combine top results to form new context
                top_texts = [r["matched_text"] for r in hop_results[:3]]
                current_context = initial_query + " " + " ".join(top_texts)
        
        return {
            "initial_query": initial_query,
            "total_hops": hops,
            "results_by_hop": results_by_hop
        }

