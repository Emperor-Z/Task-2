"""FR3, FR4, FR5: Query service for market basket analysis.

FR3: Pair frequency lookup and co-purchase threshold check
FR4: Top-K item pairs (bundles) ranked by frequency
FR5: Top-K items bought with a given item (recommendations)
"""

from typing import List, Tuple, Dict
from src.cooccurrence_graph import CooccurrenceGraph


class QueryService:
    """Query service operating on the co-occurrence graph.
    
    Provides methods for:
    - Pair frequency lookup (FR3)
    - Top-K bundle ranking (FR4)
    - Top-K item recommendations (FR5)
    """

    def __init__(self, graph: CooccurrenceGraph):
        """Initialize service with a graph instance.
        
        Args:
            graph: CooccurrenceGraph instance to query
        """
        self.graph = graph

    # ========== FR3: Pair Frequency Lookup ==========

    def pair_frequency(self, item_a: str, item_b: str) -> int:
        """Get co-purchase frequency for a pair of items.
        
        Args:
            item_a: First item
            item_b: Second item
        
        Returns:
            Number of times items were co-purchased (0 if never)
        """
        return self.graph.get_weight(item_a, item_b)

    def often_copurchased(self, item_a: str, item_b: str, threshold: int) -> bool:
        """Check if two items are often co-purchased (above threshold).
        
        Args:
            item_a: First item
            item_b: Second item
            threshold: Minimum co-purchase frequency to consider "often"
        
        Returns:
            True if items co-purchased >= threshold times, False otherwise
        """
        frequency = self.pair_frequency(item_a, item_b)
        return frequency >= threshold

    # ========== FR5: Top-K Items Bought with Item ==========

    def top_with_item(self, item: str, k: int) -> List[Tuple[str, int]]:
        """Get top K items bought with a given item (recommendations).
        
        For example: top_with_item("bread", k=5) returns items most frequently
        bought together with bread, ranked by frequency.
        
        Tie-breaking: When items have equal frequency, sort alphabetically.
        
        Args:
            item: Item to find recommendations for
            k: Maximum number of recommendations to return
        
        Returns:
            List of (item_name, frequency) tuples, sorted by:
            1. Frequency descending
            2. Item name alphabetically (tie-breaker)
        """
        # Get all neighbors of the item
        neighbors = self.graph.neighbors(item)
        
        if not neighbors:
            return []
        
        # Sort by: frequency (desc), then alphabetically
        sorted_items = sorted(
            neighbors.items(),
            key=lambda x: (-x[1], x[0])  # (-frequency, name)
        )
        
        return sorted_items[:k]

    # ========== FR4: Top-K Bundles (Pairs) Globally ==========

    def top_bundles(self, k: int) -> List[Tuple[str, str, int]]:
        """Get top K most common product bundles (item pairs) globally.
        
        Returns pairs ranked by co-purchase frequency across all transactions.
        Each unique pair appears only once (no A-B and B-A duplicates).
        
        Tie-breaking: When pairs have equal frequency, sort alphabetically
        on (item_a, item_b) in lexicographic order.
        
        Args:
            k: Maximum number of bundles to return
        
        Returns:
            List of (item_a, item_b, frequency) tuples where item_a < item_b,
            sorted by: 1. Frequency descending
                      2. Item names alphabetically (tie-breaker)
        """
        # Get all unique edges from graph
        edges = self.graph.unique_edges()
        
        if not edges:
            return []
        
        # Sort by: frequency (desc), then alphabetically (item_a, then item_b)
        sorted_edges = sorted(
            edges,
            key=lambda x: (-x[2], x[0], x[1])  # (-frequency, item_a, item_b)
        )
        
        return sorted_edges[:k]
