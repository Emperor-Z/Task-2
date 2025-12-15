"""FR6 & FR7: Text-based presentation and BFS exploration.

FR6: Format and present results in readable text format
FR7: BFS traversal with weight and depth filters
"""

from typing import List, Tuple, Dict, Set
from collections import deque
import math
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
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

    @staticmethod
    def plot_graph(
        edges: List[Tuple[str, str, int]],
        output_path: str,
        max_edges: int = 20,
        min_weight: int = 1
    ) -> str:
        """Create a simple graph visualization highlighting strongest associations.

        Args:
            edges: List of (item_a, item_b, weight) tuples.
            output_path: Where to write the PNG image.
            max_edges: Maximum number of edges to render, ranked by weight.
            min_weight: Minimum edge weight to include.

        Returns:
            The output_path written to disk.
        """
        filtered = [
            (a, b, w) for a, b, w in sorted(edges, key=lambda x: -x[2])
            if w >= min_weight
        ][:max_edges]

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.axis("off")

        if not filtered:
            ax.text(0.5, 0.5, "No edges to plot", ha="center", va="center")
            fig.savefig(output_path, bbox_inches="tight", dpi=150)
            plt.close(fig)
            return output_path

        nodes = sorted({n for edge in filtered for n in edge[:2]})
        count = len(nodes)
        angles = [2 * math.pi * i / count for i in range(count)]
        positions = {
            node: (math.cos(angle), math.sin(angle))
            for node, angle in zip(nodes, angles)
        }

        max_weight = max(w for _, _, w in filtered)

        for a, b, w in filtered:
            x1, y1 = positions[a]
            x2, y2 = positions[b]
            width = 1 + 3 * (w / max_weight if max_weight else 0)
            ax.plot([x1, x2], [y1, y2], color="#4b8bbe", linewidth=width, alpha=0.8)
            ax.text(
                (x1 + x2) / 2,
                (y1 + y2) / 2,
                str(w),
                fontsize=8,
                color="#2c3e50",
                ha="center",
                va="center",
            )

        for node in nodes:
            x, y = positions[node]
            ax.scatter(x, y, s=200, color="#fdd835", edgecolors="#333333", zorder=3)
            ax.text(x, y, node, fontsize=9, ha="center", va="center", zorder=4)

        fig.savefig(output_path, bbox_inches="tight", dpi=150)
        plt.close(fig)
        return output_path
