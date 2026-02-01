"""
Research paper search and analysis tool
"""
import json
from typing import List, Dict, Optional
import os

class PaperSearchTool:
    """Tool for searching and analyzing research papers"""
    
    def __init__(self, data_path: str = "data/research_papers.json"):
        self.data_path = data_path
        self.papers = self._load_papers()
    
    def _load_papers(self) -> List[Dict]:
        """Load research papers from JSON file"""
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
        Search papers by title, abstract, or keywords
        
        Args:
            query: Search query
            filters: Optional filters (year, field, venue, etc.)
            limit: Maximum number of results
            
        Returns:
            List of matching papers
        """
        results = []
        query_lower = query.lower()
        
        for paper in self.papers:
            # Search in multiple fields
            searchable_text = (
                paper.get("title", "").lower() + " " +
                paper.get("abstract", "").lower() + " " +
                " ".join(paper.get("keywords", [])).lower()
            )
            
            if query_lower in searchable_text:
                # Apply filters
                if filters and not self._matches_filters(paper, filters):
                    continue
                
                results.append(paper)
                
                if len(results) >= limit:
                    break
        
        return results
    
    def get_by_id(self, paper_id: str) -> Optional[Dict]:
        """Get paper by ID"""
        return next((p for p in self.papers if p["id"] == paper_id), None)
    
    def find_related_papers(
        self,
        paper_id: str,
        method: str = "citations",
        limit: int = 10
    ) -> List[Dict]:
        """
        Find papers related to a given paper
        
        Args:
            paper_id: ID of the reference paper
            method: 'citations' or 'keywords'
            limit: Maximum number of results
            
        Returns:
            List of related papers
        """
        paper = self.get_by_id(paper_id)
        if not paper:
            return []
        
        if method == "citations":
            # Papers cited by this paper
            cited_ids = paper.get("citations", [])
            related = [self.get_by_id(pid) for pid in cited_ids]
            related = [p for p in related if p is not None]
            
            # Papers citing this paper
            citing = [p for p in self.papers 
                     if paper_id in p.get("citations", [])]
            related.extend(citing)
            
        elif method == "keywords":
            # Papers with overlapping keywords
            paper_keywords = set(paper.get("keywords", []))
            related = []
            
            for p in self.papers:
                if p["id"] == paper_id:
                    continue
                
                p_keywords = set(p.get("keywords", []))
                overlap = len(paper_keywords & p_keywords)
                
                if overlap > 0:
                    p["keyword_overlap"] = overlap
                    related.append(p)
            
            related.sort(key=lambda x: x.get("keyword_overlap", 0), reverse=True)
        
        else:
            return []
        
        return related[:limit]
    
    def get_citation_network(self, paper_id: str, depth: int = 2) -> Dict:
        """
        Build citation network around a paper
        
        Args:
            paper_id: Starting paper ID
            depth: How many levels to traverse
            
        Returns:
            Dict representing citation network
        """
        visited = set()
        network = {"nodes": [], "edges": []}
        
        def traverse(pid, current_depth):
            if current_depth > depth or pid in visited:
                return
            
            visited.add(pid)
            paper = self.get_by_id(pid)
            
            if not paper:
                return
            
            network["nodes"].append({
                "id": pid,
                "title": paper["title"],
                "year": paper["year"],
                "citations_count": paper.get("citations_count", 0)
            })
            
            # Add edges for citations
            for cited_id in paper.get("citations", []):
                network["edges"].append({
                    "from": pid,
                    "to": cited_id,
                    "type": "cites"
                })
                traverse(cited_id, current_depth + 1)
        
        traverse(paper_id, 0)
        return network
    
    def analyze_field_trends(self, field: str, year_range: Optional[tuple] = None) -> Dict:
        """Analyze research trends in a field"""
        # Filter papers by field
        field_papers = [p for p in self.papers if p.get("field") == field]
        
        # Apply year range if specified
        if year_range:
            field_papers = [p for p in field_papers 
                          if year_range[0] <= p["year"] <= year_range[1]]
        
        # Count by year
        papers_by_year = {}
        for paper in field_papers:
            year = paper["year"]
            papers_by_year[year] = papers_by_year.get(year, 0) + 1
        
        # Top venues
        venues = {}
        for paper in field_papers:
            venue = paper.get("venue", "Unknown")
            venues[venue] = venues.get(venue, 0) + 1
        
        top_venues = sorted(venues.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Top keywords
        all_keywords = []
        for paper in field_papers:
            all_keywords.extend(paper.get("keywords", []))
        
        keyword_counts = {}
        for kw in all_keywords:
            keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
        
        top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # Citation statistics
        total_citations = sum(p.get("citations_count", 0) for p in field_papers)
        
        return {
            "field": field,
            "total_papers": len(field_papers),
            "year_range": (min(p["year"] for p in field_papers) if field_papers else None,
                          max(p["year"] for p in field_papers) if field_papers else None),
            "papers_by_year": papers_by_year,
            "top_venues": [{"venue": v, "count": c} for v, c in top_venues],
            "top_keywords": [{"keyword": k, "count": c} for k, c in top_keywords],
            "citations": {
                "total": total_citations,
                "average": total_citations / len(field_papers) if field_papers else 0
            }
        }
    
    def compare_methodologies(self, paper_ids: List[str]) -> Dict:
        """Compare methodologies across multiple papers"""
        papers = [self.get_by_id(pid) for pid in paper_ids]
        papers = [p for p in papers if p is not None]
        
        if not papers:
            return {"error": "No valid papers found"}
        
        comparison = {
            "papers": [],
            "common_keywords": [],
            "methodology_distribution": {}
        }
        
        all_keywords = []
        for paper in papers:
            comparison["papers"].append({
                "id": paper["id"],
                "title": paper["title"],
                "year": paper["year"],
                "methodology": paper.get("methodology", "Unknown"),
                "keywords": paper.get("keywords", [])
            })
            
            all_keywords.append(set(paper.get("keywords", [])))
            
            # Count methodologies
            method = paper.get("methodology", "Unknown")
            comparison["methodology_distribution"][method] = \
                comparison["methodology_distribution"].get(method, 0) + 1
        
        # Find common keywords
        if all_keywords:
            common = set.intersection(*all_keywords)
            comparison["common_keywords"] = list(common)
        
        return comparison
    
    def _matches_filters(self, paper: Dict, filters: Dict) -> bool:
        """Check if paper matches all filters"""
        for key, value in filters.items():
            if key == "year_min":
                if paper.get("year", 0) < value:
                    return False
            elif key == "year_max":
                if paper.get("year", 9999) > value:
                    return False
            elif key == "min_citations":
                if paper.get("citations_count", 0) < value:
                    return False
            elif isinstance(value, list):
                if paper.get(key) not in value:
                    return False
            else:
                if paper.get(key) != value:
                    return False
        
        return True

