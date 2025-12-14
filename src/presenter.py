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
        if not bundles:
            return "No bundles found."

        lines = ["=" * 60, "TOP PRODUCT BUNDLES (Item Pairs)", "=" * 60]
        lines.append(f"{'Rank':<6} {'Item 1':<20} {'Item 2':<20} {'Frequency':<8}")
        lines.append("-" * 60)

        for rank, (item_a, item_b, freq) in enumerate(bundles, 1):
            lines.append(f"{rank:<6} {item_a:<20} {item_b:<20} {freq:<8}")

        lines.append("=" * 60)
        return "\n".join(lines)

    @staticmethod
    def format_recommendations(items: List[Tuple[str, int]], item_name: str) -> str:
        """Format item recommendations for a given item.
        
        Args:
            items: List of (item_name, frequency) tuples
            item_name: The reference item
        
        Returns:
            Formatted text string (suitable for CLI output)
        """
        if not items:
            return f"No items found to recommend with '{item_name}'."

        lines = ["=" * 60, f"TOP ITEMS BOUGHT WITH: {item_name.upper()}", "=" * 60]
        lines.append(f"{'Rank':<6} {'Item':<30} {'Co-Purchases':<8}")
        lines.append("-" * 60)

        for rank, (item, freq) in enumerate(items, 1):
            lines.append(f"{rank:<6} {item:<30} {freq:<8}")

        lines.append("=" * 60)
        return "\n".join(lines)

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
