"""Unit tests for FR3, FR4, FR5: Query service (lookup, bundles, recommendations).

FR3: Pair frequency lookup and co-purchase threshold check
FR4: Top-K bundles (item pairs) globally
FR5: Top-K items bought with a given item (recommendations)
"""

import unittest


class TestQueryService(unittest.TestCase):
    """Test cases for QueryService queries on the graph."""

    def setUp(self):
        """Set up graph with sample data for queries."""
        from src.cooccurrence_graph import CooccurrenceGraph
        from src.query_service import QueryService
        
        self.graph = CooccurrenceGraph()
        # Build a simple graph:
        # bread—milk (weight 3), bread—eggs (weight 2), milk—eggs (weight 1), bread—butter (weight 1)
        self.graph.update_from_basket(["bread", "milk"])
        self.graph.update_from_basket(["bread", "milk"])
        self.graph.update_from_basket(["bread", "milk"])
        self.graph.update_from_basket(["bread", "eggs"])
        self.graph.update_from_basket(["bread", "eggs"])
        self.graph.update_from_basket(["milk", "eggs"])
        self.graph.update_from_basket(["bread", "butter"])
        
        self.service = QueryService(self.graph)

    # ========== FR3 Tests ==========

    def test_pair_frequency_returns_zero_for_missing_pair(self):
        """FR3-T1: Missing pair returns 0."""
        # Act
        freq = self.service.pair_frequency("milk", "butter")

        # Assert
        self.assertEqual(freq, 0, "Never co-purchased pair should return 0")

    def test_pair_frequency_zero_when_item_not_in_graph(self):
        """FR3-T1a: Unknown item returns 0 frequency."""
        freq = self.service.pair_frequency("unknown_item", "bread")

        self.assertEqual(freq, 0)

    def test_pair_frequency_returns_correct_count(self):
        """FR3-T2: Known pair returns correct count."""
        # Act
        freq_bread_milk = self.service.pair_frequency("bread", "milk")
        freq_bread_eggs = self.service.pair_frequency("bread", "eggs")

        # Assert
        self.assertEqual(freq_bread_milk, 3, "bread-milk seen 3 times")
        self.assertEqual(freq_bread_eggs, 2, "bread-eggs seen 2 times")

    def test_often_copurchased_threshold_check(self):
        """FR3-T3: Threshold check returns True if weight >= threshold."""
        # Act
        is_often_3 = self.service.often_copurchased("bread", "milk", threshold=3)
        is_often_4 = self.service.often_copurchased("bread", "milk", threshold=4)
        is_often_2 = self.service.often_copurchased("bread", "eggs", threshold=2)
        is_often_3_eggs = self.service.often_copurchased("bread", "eggs", threshold=3)

        # Assert
        self.assertTrue(is_often_3, "weight 3 >= threshold 3")
        self.assertFalse(is_often_4, "weight 3 < threshold 4")
        self.assertTrue(is_often_2, "weight 2 >= threshold 2")
        self.assertFalse(is_often_3_eggs, "weight 2 < threshold 3")

    def test_often_copurchased_returns_false_for_missing_pair(self):
        """FR3-T3a: Missing pair should not meet threshold."""
        is_often = self.service.often_copurchased("milk", "butter", threshold=1)

        self.assertFalse(is_often)

    # ========== FR5 Tests ==========

    def test_top_with_item_sorted_descending(self):
        """FR5-T1: Results sorted by weight descending."""
        # Act
        top_items = self.service.top_with_item("bread", k=5)

        # Assert
        # bread has: milk (3), eggs (2), butter (1)
        self.assertEqual(len(top_items), 3)
        self.assertEqual(top_items[0], ("milk", 3), "milk is most frequent with bread")
        self.assertEqual(top_items[1], ("eggs", 2))
        self.assertEqual(top_items[2], ("butter", 1))

    def test_top_with_item_limit_to_k(self):
        """FR5-T2: Results limited to K items."""
        # Act
        top_2 = self.service.top_with_item("bread", k=2)
        top_1 = self.service.top_with_item("bread", k=1)
        top_10 = self.service.top_with_item("bread", k=10)

        # Assert
        self.assertEqual(len(top_2), 2, "k=2 should return 2 items")
        self.assertEqual(len(top_1), 1, "k=1 should return 1 item")
        self.assertEqual(len(top_10), 3, "k=10 but only 3 neighbors exist")

    def test_top_with_item_missing_item_returns_empty(self):
        """FR5-T3: Missing item returns empty list."""
        # Act
        top_items = self.service.top_with_item("nonexistent_item", k=5)

        # Assert
        self.assertEqual(top_items, [], "Missing item should return empty list")

    def test_top_with_item_handles_zero_neighbors(self):
        """FR5-T3a: Item with no neighbors returns empty list."""
        from src.cooccurrence_graph import CooccurrenceGraph
        from src.query_service import QueryService

        graph = CooccurrenceGraph()
        graph.update_from_basket(["solo"])
        service = QueryService(graph)

        self.assertEqual(service.top_with_item("solo", k=3), [])

    def test_top_with_item_tie_break_alphabetical(self):
        """FR5-T4: Tie-break by alphabetical order (secondary sort)."""
        # Arrange: Create graph with ties
        from src.cooccurrence_graph import CooccurrenceGraph
        from src.query_service import QueryService
        
        graph = CooccurrenceGraph()
        # Create: bread—apple (2), bread—zebra (2) - tie!
        graph.update_from_basket(["bread", "apple"])
        graph.update_from_basket(["bread", "apple"])
        graph.update_from_basket(["bread", "zebra"])
        graph.update_from_basket(["bread", "zebra"])
        
        service = QueryService(graph)
        
        # Act
        top_items = service.top_with_item("bread", k=5)

        # Assert
        # Both have weight 2, should be ordered alphabetically
        self.assertEqual(len(top_items), 2)
        self.assertEqual(top_items[0][0], "apple", "apple < zebra alphabetically")
        self.assertEqual(top_items[1][0], "zebra")

    # ========== FR4 Tests ==========

    def test_top_bundles_unique_edges_no_duplicates(self):
        """FR4-T1: Unique edges only (avoid A-B and B-A double-count)."""
        # Act
        bundles = self.service.top_bundles(k=10)

        # Assert
        # Should have exactly 4 unique pairs, not 8
        self.assertEqual(len(bundles), 4, "Should have 4 unique pairs")
        
        # Check no duplicates (reversed pairs)
        pairs_set = set()
        for item_a, item_b, weight in bundles:
            # Canonical form: sorted pair
            pair = tuple(sorted([item_a, item_b]))
            self.assertNotIn(pair, pairs_set, f"Pair {pair} appears twice")
            pairs_set.add(pair)

    def test_top_bundles_empty_graph_returns_empty(self):
        """FR4-T0: top_bundles on empty graph returns []."""
        from src.cooccurrence_graph import CooccurrenceGraph
        from src.query_service import QueryService

        empty_service = QueryService(CooccurrenceGraph())

        self.assertEqual(empty_service.top_bundles(k=5), [])

    def test_top_bundles_sorted_descending(self):
        """FR4-T2: Bundles sorted by weight descending."""
        # Act
        bundles = self.service.top_bundles(k=10)

        # Assert
        # Expected order: bread-milk (3), bread-eggs (2), bread-butter (1), milk-eggs (1)
        self.assertEqual(bundles[0][2], 3, "First bundle should have weight 3")
        self.assertEqual(bundles[1][2], 2, "Second bundle should have weight 2")
        self.assertGreaterEqual(bundles[0][2], bundles[1][2])
        self.assertGreaterEqual(bundles[1][2], bundles[2][2])

    def test_top_bundles_limit_to_k(self):
        """FR4-T3: Limited to K results."""
        # Act
        top_2 = self.service.top_bundles(k=2)
        top_1 = self.service.top_bundles(k=1)
        top_10 = self.service.top_bundles(k=10)

        # Assert
        self.assertEqual(len(top_2), 2, "k=2 should return 2 bundles")
        self.assertEqual(len(top_1), 1, "k=1 should return 1 bundle")
        self.assertEqual(len(top_10), 4, "k=10 but only 4 bundles exist")

    def test_top_bundles_tie_break_alphabetical(self):
        """FR4-T4: Tie-break alphabetically when weights are equal."""
        # Arrange: Create graph with tied weights
        from src.cooccurrence_graph import CooccurrenceGraph
        from src.query_service import QueryService
        
        graph = CooccurrenceGraph()
        # Create: apple-zebra (2), apple-yankee (2) - tie!
        graph.update_from_basket(["apple", "zebra"])
        graph.update_from_basket(["apple", "zebra"])
        graph.update_from_basket(["apple", "yankee"])
        graph.update_from_basket(["apple", "yankee"])
        
        service = QueryService(graph)
        
        # Act
        bundles = service.top_bundles(k=10)

        # Assert
        # Both have weight 2, should be ordered alphabetically (apple-yankee before apple-zebra)
        self.assertEqual(len(bundles), 2)
        self.assertEqual((bundles[0][0], bundles[0][1]), ("apple", "yankee"))
        self.assertEqual((bundles[1][0], bundles[1][1]), ("apple", "zebra"))


if __name__ == '__main__':
    unittest.main()
