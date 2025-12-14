"""FR2 & FR8: Weighted undirected graph for co-occurrence counts.

Stores item co-occurrences as an adjacency list (nested dicts).
Supports incremental updates when new transactions arrive (no full rebuild).
"""

from typing import List, Dict, Tuple


class CooccurrenceGraph:
    """Weighted undirected graph of item co-occurrences.
    
    Represented as adjacency list: graph[item_a][item_b] = weight
    where weight is the number of times items were bought together.
    
    Properties:
    - Undirected: graph[a][b] == graph[b][a] (symmetric)
    - No self-edges: never adds (item, item) pairs
    - Weighted: counts how many times each pair co-occurred
    """

    def __init__(self):
        """Initialize empty graph."""
        self.graph: Dict[str, Dict[str, int]] = {}

    def update_from_basket(self, basket: List[str]) -> None:
        """Update graph with co-occurrences from one basket (transaction)."""
        for i in range(len(basket)):
            for j in range(i + 1, len(basket)):
                item_a = basket[i]
                item_b = basket[j]

                if item_a == item_b:
                    continue

                if item_a not in self.graph:
                    self.graph[item_a] = {}
                if item_b not in self.graph:
                    self.graph[item_b] = {}

                self.graph[item_a][item_b] = self.graph[item_a].get(item_b, 0) + 1
                self.graph[item_b][item_a] = self.graph[item_b].get(item_a, 0) + 1

    def get_weight(self, item_a: str, item_b: str) -> int:
        """Get co-purchase frequency for pair (item_a, item_b).
        
        Args:
            item_a: First item
            item_b: Second item
        
        Returns:
            Number of times items were co-purchased (0 if never/not exist)
        """
        if item_a not in self.graph:
            return 0
        return self.graph[item_a].get(item_b, 0)

    def neighbors(self, item: str) -> Dict[str, int]:
        """Get all items bought with a given item and their co-purchase counts.
        
        Args:
            item: Item to find neighbors for
        
        Returns:
            Dictionary mapping neighbor items to co-purchase frequency.
            Empty dict if item not in graph.
        """
        return self.graph.get(item, {})

    def unique_edges(self) -> List[Tuple[str, str, int]]:
        """Return all unique edges in graph (avoiding A-B and B-A duplicates).
        
        Returns:
            List of (item_a, item_b, weight) tuples where item_a < item_b (lexicographic).
            This ensures each pair appears only once (no duplicates).
        """
        edges: List[Tuple[str, str, int]] = []
        seen = set()

        for item_a, neighbors in self.graph.items():
            for item_b, weight in neighbors.items():
                pair = tuple(sorted([item_a, item_b]))
                if pair in seen:
                    continue

                seen.add(pair)
                edges.append((pair[0], pair[1], weight))

        return edges
