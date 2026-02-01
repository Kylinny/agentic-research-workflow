"""
Citation tracking and analysis tool for research papers
"""
from typing import List, Dict, Set, Optional
import json
import os

class CitationTrackerTool:
    """Tool for tracking and analyzing citation relationships"""
    
    def __init__(self, data_path: str = "data/research_papers.json"):
        self.data_path = data_path
        self.papers = self._load_papers()
        self._build_reverse_citations()
    
    def _load_papers(self) -> List[Dict]:
        """Load research papers"""
        if not os.path.exists(self.data_path):
            return []
        
        with open(self.data_path, 'r') as f:
            return json.load(f)
    
    def _build_reverse_citations(self):
        """Build reverse citation index (who cites whom)"""
        self.cited_by = {}
        
        for paper in self.papers:
            paper_id = paper["id"]
            for cited_id in paper.get("citations", []):
                if cited_id not in self.cited_by:
                    self.cited_by[cited_id] = []
                self.cited_by[cited_id].append(paper_id)
    
    def get_citations(self, paper_id: str) -> List[str]:
        """Get papers cited by this paper"""
        paper = next((p for p in self.papers if p["id"] == paper_id), None)
        return paper.get("citations", []) if paper else []
    
    def get_cited_by(self, paper_id: str) -> List[str]:
        """Get papers that cite this paper"""
        return self.cited_by.get(paper_id, [])
    
    def get_citation_count(self, paper_id: str) -> int:
        """Get number of citations for a paper"""
        return len(self.get_cited_by(paper_id))
    
    def find_influential_papers(
        self,
        min_citations: int = 10,
        limit: int = 20
    ) -> List[Dict]:
        """
        Find most influential papers based on citation count
        
        Args:
            min_citations: Minimum citation threshold
            limit: Maximum number of results
            
        Returns:
            List of papers sorted by influence
        """
        papers_with_counts = []
        
        for paper in self.papers:
            paper_id = paper["id"]
            citation_count = self.get_citation_count(paper_id)
            
            if citation_count >= min_citations:
                papers_with_counts.append({
                    **paper,
                    "citation_count_computed": citation_count,
                    "h_index_contribution": min(citation_count, 1)
                })
        
        # Sort by citation count
        papers_with_counts.sort(
            key=lambda x: x["citation_count_computed"],
            reverse=True
        )
        
        return papers_with_counts[:limit]
    
    def trace_citation_chain(
        self,
        start_paper_id: str,
        end_paper_id: str,
        max_depth: int = 5
    ) -> List[List[str]]:
        """
        Find citation chains between two papers
        
        Args:
            start_paper_id: Starting paper
            end_paper_id: Target paper
            max_depth: Maximum chain length
            
        Returns:
            List of paths (each path is a list of paper IDs)
        """
        paths = []
        
        def dfs(current_id: str, target_id: str, path: List[str], depth: int):
            if depth > max_depth:
                return
            
            if current_id == target_id:
                paths.append(path + [current_id])
                return
            
            if current_id in path:  # Avoid cycles
                return
            
            # Explore citations
            citations = self.get_citations(current_id)
            for cited_id in citations:
                dfs(cited_id, target_id, path + [current_id], depth + 1)
        
        dfs(start_paper_id, end_paper_id, [], 0)
        return paths
    
    def find_common_citations(self, paper_ids: List[str]) -> Dict:
        """
        Find papers commonly cited by a set of papers
        
        Args:
            paper_ids: List of paper IDs to compare
            
        Returns:
            Dict with common citations and statistics
        """
        if not paper_ids:
            return {"error": "No paper IDs provided"}
        
        # Get all citation sets
        citation_sets = []
        for paper_id in paper_ids:
            citations = set(self.get_citations(paper_id))
            citation_sets.append(citations)
        
        # Find intersection
        common = set.intersection(*citation_sets) if citation_sets else set()
        
        # Count frequency across all papers
        citation_freq = {}
        all_citations = set().union(*citation_sets)
        
        for cited_id in all_citations:
            count = sum(1 for cset in citation_sets if cited_id in cset)
            citation_freq[cited_id] = count
        
        # Sort by frequency
        sorted_citations = sorted(
            citation_freq.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            "input_papers": len(paper_ids),
            "common_citations": list(common),
            "common_count": len(common),
            "citation_frequency": [
                {"paper_id": cid, "cited_by_count": count}
                for cid, count in sorted_citations
            ]
        }
    
    def build_citation_graph(
        self,
        seed_papers: List[str],
        max_depth: int = 2
    ) -> Dict:
        """
        Build a citation graph starting from seed papers
        
        Args:
            seed_papers: List of starting paper IDs
            max_depth: How many hops to traverse
            
        Returns:
            Dict representing the citation graph
        """
        visited = set()
        nodes = []
        edges = []
        
        def traverse(paper_id: str, depth: int):
            if depth > max_depth or paper_id in visited:
                return
            
            visited.add(paper_id)
            
            # Get paper details
            paper = next((p for p in self.papers if p["id"] == paper_id), None)
            if not paper:
                return
            
            nodes.append({
                "id": paper_id,
                "title": paper["title"],
                "year": paper["year"],
                "depth": depth
            })
            
            # Add citation edges
            citations = self.get_citations(paper_id)
            for cited_id in citations:
                edges.append({
                    "from": paper_id,
                    "to": cited_id,
                    "type": "cites"
                })
                traverse(cited_id, depth + 1)
        
        # Start from seed papers
        for seed_id in seed_papers:
            traverse(seed_id, 0)
        
        return {
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges)
        }
    
    def calculate_impact_metrics(self, paper_id: str) -> Dict:
        """
        Calculate various impact metrics for a paper
        
        Args:
            paper_id: Paper to analyze
            
        Returns:
            Dict with impact metrics
        """
        paper = next((p for p in self.papers if p["id"] == paper_id), None)
        if not paper:
            return {"error": "Paper not found"}
        
        # Direct citations
        direct_citations = self.get_cited_by(paper_id)
        
        # Second-order citations (papers citing papers that cite this)
        second_order = set()
        for citing_id in direct_citations:
            second_order.update(self.get_cited_by(citing_id))
        second_order.discard(paper_id)
        
        # Calculate citation velocity (citations per year since publication)
        current_year = 2025
        years_since_pub = current_year - paper.get("year", current_year)
        citation_velocity = len(direct_citations) / max(years_since_pub, 1)
        
        # Find most influential papers citing this one
        influential_citers = []
        for citing_id in direct_citations:
            citing_paper = next((p for p in self.papers if p["id"] == citing_id), None)
            if citing_paper:
                citer_citations = len(self.get_cited_by(citing_id))
                influential_citers.append({
                    "id": citing_id,
                    "title": citing_paper["title"],
                    "citations": citer_citations
                })
        
        influential_citers.sort(key=lambda x: x["citations"], reverse=True)
        
        return {
            "paper_id": paper_id,
            "title": paper["title"],
            "year": paper["year"],
            "direct_citations": len(direct_citations),
            "second_order_citations": len(second_order),
            "citation_velocity": citation_velocity,
            "top_influential_citers": influential_citers[:10],
            "impact_score": (
                len(direct_citations) * 1.0 +
                len(second_order) * 0.1 +
                citation_velocity * 5.0
            )
        }

