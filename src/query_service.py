"""FR3, FR4, FR5, FR7: Query service for market basket analysis.

FR3: Pair frequency lookup and co-purchase threshold check
FR4: Top-K item pairs (bundles) ranked by frequency
FR5: Top-K items bought with a given item (recommendations)
FR7: BFS exploration with filters (min_weight, max_depth)
"""

from typing import List, Tuple, Dict, Set
from collections import deque
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
        return self.pair_frequency(item_a, item_b) >= threshold

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
        neighbors = self.graph.neighbors(item)
        if not neighbors:
            return []

        sorted_items = sorted(neighbors.items(), key=lambda x: (-x[1], x[0]))
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
        edges = self.graph.unique_edges()
        if not edges:
            return []

        sorted_edges = sorted(edges, key=lambda x: (-x[2], x[0], x[1]))
        return sorted_edges[:k]

    # ========== FR7: BFS Exploration ==========

    def bfs_related(
        self,
        start_item: str,
        max_depth: int = 2,
        min_weight: int = 1
    ) -> Dict[str, Dict[int, Set[str]]]:
        """Explore items related to a start item via BFS (breadth-first search).
        
        Uses BFS to explore item relationships at multiple hops, with filters:
        - max_depth: Maximum hop distance (1 = direct neighbors only)
        - min_weight: Minimum co-purchase frequency to traverse an edge
        
        Prevents infinite loops with visited set tracking.
        
        Args:
            start_item: Item to explore from
            max_depth: Maximum relationship depth (hops)
            min_weight: Minimum edge weight to traverse
        
        Returns:
            Dictionary structure:
            {
                start_item: {
                    1: {items at distance 1},
                    2: {items at distance 2},
                    ...
                }
            }
        """
        if start_item not in self.graph.graph:
            return {start_item: {}}

        result: Dict[str, Dict[int, Set[str]]] = {start_item: {}}
        visited = {start_item}
        queue = deque([(start_item, 0)])

        while queue:
            current_item, depth = queue.popleft()
            if depth >= max_depth:
                continue

            neighbors = self.graph.neighbors(current_item)
            for neighbor, weight in neighbors.items():
                if neighbor in visited:
                    continue
                if weight < min_weight:
                    continue

                visited.add(neighbor)
                next_depth = depth + 1
                result[start_item].setdefault(next_depth, set()).add(neighbor)
                queue.append((neighbor, next_depth))

        return result
