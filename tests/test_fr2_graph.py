"""Unit tests for FR2 & FR8: Graph construction and incremental updates.

Tests verify co-occurrence graph construction from baskets, with incremental
update support. Graph is an adjacency list (nested dicts) with:
- Undirected edges (A-B symmetry)
- Weighted counts (co-occurrence frequency)
- No self-edges (item paired with itself)
"""

import unittest


class TestCooccurrenceGraph(unittest.TestCase):
    """Test cases for CooccurrenceGraph class."""

    def test_new_graph_returns_zero_for_unseen_pair(self):
        """FR2-T1: New graph returns 0 for pair that hasn't been seen."""
        # Arrange
        from src.cooccurrence_graph import CooccurrenceGraph
        graph = CooccurrenceGraph()

        # Act
        weight = graph.get_weight("bread", "milk")

        # Assert
        self.assertEqual(weight, 0, "Unseen pair should return weight 0")

    def test_get_weight_handles_missing_items(self):
        """FR2-T1b: get_weight returns 0 when either item missing."""
        from src.cooccurrence_graph import CooccurrenceGraph
        graph = CooccurrenceGraph()

        self.assertEqual(graph.get_weight("bread", "missing"), 0)

    def test_update_creates_nodes_for_items(self):
        """FR2-T0: Update adds items to internal adjacency structure."""
        from src.cooccurrence_graph import CooccurrenceGraph
        graph = CooccurrenceGraph()

        graph.update_from_basket(["bread", "milk"])

        self.assertIn("bread", graph.graph)
        self.assertIn("milk", graph.graph)

    def test_update_sets_weight_for_pair(self):
        """FR2-T1c: update_from_basket sets weight to 1 for new pair."""
        from src.cooccurrence_graph import CooccurrenceGraph
        graph = CooccurrenceGraph()

        graph.update_from_basket(["bread", "milk"])

        self.assertEqual(graph.get_weight("bread", "milk"), 1)

    def test_basket_increments_both_directions(self):
        """FR2-T2: Basket [A, B] increments both A→B and B→A (symmetry)."""
        # Arrange
        from src.cooccurrence_graph import CooccurrenceGraph
        graph = CooccurrenceGraph()
        basket = ["bread", "milk"]

        # Act
        graph.update_from_basket(basket)

        # Assert
        # Check both directions exist and are equal (undirected)
        weight_ab = graph.get_weight("bread", "milk")
        weight_ba = graph.get_weight("milk", "bread")
        
        self.assertEqual(weight_ab, 1, "bread→milk should have weight 1")
        self.assertEqual(weight_ba, 1, "milk→bread should have weight 1")
        self.assertEqual(weight_ab, weight_ba, "Graph should be undirected (symmetric)")

    def test_basket_with_three_items_increments_all_pairs(self):
        """FR2-T3: Basket [A, B, C] increments all 3 pairs (complete graph)."""
        # Arrange
        from src.cooccurrence_graph import CooccurrenceGraph
        graph = CooccurrenceGraph()
        basket = ["bread", "milk", "eggs"]

        # Act
        graph.update_from_basket(basket)

        # Assert
        # All 3 pairs should exist with weight 1
        pairs = [
            ("bread", "milk"),
            ("bread", "eggs"),
            ("milk", "eggs"),
        ]
        
        for item_a, item_b in pairs:
            weight_ab = graph.get_weight(item_a, item_b)
            weight_ba = graph.get_weight(item_b, item_a)
            self.assertEqual(
                weight_ab, 1,
                f"Pair ({item_a}, {item_b}) should have weight 1"
            )
            self.assertEqual(
                weight_ab, weight_ba,
                f"Pair ({item_a}, {item_b}) should be symmetric"
            )

    def test_neighbors_empty_for_missing_item(self):
        """FR2-T5a: neighbors returns empty dict when item missing."""
        from src.cooccurrence_graph import CooccurrenceGraph
        graph = CooccurrenceGraph()

        self.assertEqual(graph.neighbors("unknown"), {})

    def test_no_self_edges(self):
        """FR2-T4: Item paired with itself is not added (no self-edges)."""
        # Arrange
        from src.cooccurrence_graph import CooccurrenceGraph
        graph = CooccurrenceGraph()
        basket = ["bread", "milk"]

        # Act
        graph.update_from_basket(basket)

        # Assert
        # Self-edges should not exist
        self.assertEqual(
            graph.get_weight("bread", "bread"), 0,
            "Self-edge bread→bread should not exist"
        )
        self.assertEqual(
            graph.get_weight("milk", "milk"), 0,
            "Self-edge milk→milk should not exist"
        )

    def test_incremental_updates_accumulate(self):
        """FR8-T1: Multiple baskets incrementally update co-occurrence counts."""
        # Arrange
        from src.cooccurrence_graph import CooccurrenceGraph
        graph = CooccurrenceGraph()
        
        # Act
        graph.update_from_basket(["bread", "milk"])  # First basket
        graph.update_from_basket(["bread", "milk"])  # Second basket
        graph.update_from_basket(["bread", "eggs"])  # Third basket

        # Assert
        # bread-milk should have been seen twice
        self.assertEqual(
            graph.get_weight("bread", "milk"), 2,
            "bread-milk seen twice should have weight 2"
        )
        # bread-eggs should have been seen once
        self.assertEqual(
            graph.get_weight("bread", "eggs"), 1,
            "bread-eggs seen once should have weight 1"
        )
        # milk-eggs should not exist
        self.assertEqual(
            graph.get_weight("milk", "eggs"), 0,
            "milk-eggs never co-purchased should have weight 0"
        )

    def test_neighbors_returns_correct_cohabitants(self):
        """FR2-T5: neighbors() returns all items bought with a given item."""
        # Arrange
        from src.cooccurrence_graph import CooccurrenceGraph
        graph = CooccurrenceGraph()
        graph.update_from_basket(["bread", "milk", "eggs"])
        graph.update_from_basket(["bread", "butter"])

        # Act
        bread_neighbors = graph.neighbors("bread")

        # Assert
        self.assertEqual(len(bread_neighbors), 3, "Bread bought with 3 items")
        self.assertEqual(bread_neighbors["milk"], 1)
        self.assertEqual(bread_neighbors["eggs"], 1)
        self.assertEqual(bread_neighbors["butter"], 1)

    def test_unique_edges_contains_all_pairs(self):
        """FR2-T6: unique_edges() returns all unique pairs (no duplicates)."""
        # Arrange
        from src.cooccurrence_graph import CooccurrenceGraph
        graph = CooccurrenceGraph()
        graph.update_from_basket(["bread", "milk", "eggs"])

        # Act
        edges = graph.unique_edges()

        # Assert
        self.assertEqual(len(edges), 3, "Should have 3 unique pairs")
        
        # Verify edges are tuples of (item_a, item_b, weight) with item_a < item_b
        for item_a, item_b, weight in edges:
            self.assertLess(
                item_a, item_b,
                f"Edges should be unique (a < b): got ({item_a}, {item_b})"
            )
            self.assertEqual(weight, 1)


if __name__ == '__main__':
    unittest.main()
