"""FR6 & FR7: Text-based presentation and BFS exploration.

FR6: Format and present results in readable text format
FR7: BFS traversal with weight and depth filters
"""

from typing import List, Tuple, Dict, Set
from collections import deque
from src.cooccurrence_graph import CooccurrenceGraph


class Presenter:
    """Text-based formatter for market basket analysis results."""

    @staticmethod
    def format_top_bundles(bundles: List[Tuple[str, str, int]]) -> str:
        """Format top bundles as readable text output.
        
        Args:
            bundles: List of (item_a, item_b, frequency) tuples
        
        Returns:
            Formatted text string (suitable for CLI output)
        """
        raise NotImplementedError("format_top_bundles not implemented yet")

    @staticmethod
    def format_recommendations(items: List[Tuple[str, int]], item_name: str) -> str:
        """Format item recommendations for a given item.
        
        Args:
            items: List of (item_name, frequency) tuples
            item_name: The reference item
        
        Returns:
            Formatted text string (suitable for CLI output)
        """
        raise NotImplementedError("format_recommendations not implemented yet")

    @staticmethod
    def format_pair(item_a: str, item_b: str, weight: int) -> str:
        """Format a single pair for display.
        
        Args:
            item_a: First item
            item_b: Second item
            weight: Co-purchase frequency
        
        Returns:
            Formatted string
        """
        return f"{item_a} + {item_b}: {weight} co-purchases"
