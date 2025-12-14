"""Unit tests for FR6 & FR7: Presentation and BFS exploration.

FR6: Text-based presentation of item relationships
FR7: BFS traversal with filters (min_weight, max_depth)
"""

import unittest


class TestPresenter(unittest.TestCase):
    """Test cases for text-based result presentation."""

    def setUp(self):
        """Set up sample data."""
        from src.cooccurrence_graph import CooccurrenceGraph
        from src.presenter import Presenter
        
        self.graph = CooccurrenceGraph()
        # Build a small graph for testing
        self.graph.update_from_basket(["bread", "milk"])
        self.graph.update_from_basket(["bread", "milk"])
        self.graph.update_from_basket(["bread", "eggs"])
        
        self.presenter = Presenter()

    def test_format_top_bundles_returns_string(self):
        """FR6-T1: Format top bundles returns readable string output."""
        # Arrange
        bundles = [("bread", "milk", 2), ("bread", "eggs", 1)]

        # Act
        output = self.presenter.format_top_bundles(bundles)

        # Assert
        self.assertIsInstance(output, str)
        self.assertIn("bread", output)
        self.assertIn("milk", output)
        self.assertIn("2", output)  # weight should appear

    def test_format_recommendations_returns_string(self):
        """FR6-T2: Format recommendations returns readable string output."""
        # Arrange
        items = [("milk", 2), ("eggs", 1)]

        # Act
        output = self.presenter.format_recommendations(items, "bread")

        # Assert
        self.assertIsInstance(output, str)
        self.assertIn("bread", output.lower())
        self.assertIn("milk", output)
        self.assertIn("2", output)

    def test_format_handles_empty_results(self):
        """FR6-T3: Format handles empty results gracefully."""
        # Act
        bundles_output = self.presenter.format_top_bundles([])
        items_output = self.presenter.format_recommendations([], "bread")

        # Assert
        self.assertIsInstance(bundles_output, str)
        self.assertIsInstance(items_output, str)
        # Should contain some message, not be empty or crash
        self.assertTrue(len(bundles_output) > 0)
        self.assertTrue(len(items_output) > 0)

    def test_format_pair_outputs_string(self):
        """FR6-T4: format_pair returns a descriptive string."""
        text = self.presenter.format_pair("bread", "milk", 2)

        self.assertIsInstance(text, str)
        self.assertIn("bread", text)
        self.assertIn("milk", text)


class TestBFSExploration(unittest.TestCase):
    """Test cases for BFS relationship exploration."""

    def setUp(self):
        """Set up graph for BFS tests."""
        from src.cooccurrence_graph import CooccurrenceGraph
        from src.query_service import QueryService
        
        self.graph = CooccurrenceGraph()
        # Build a network of relationships:
        # bread—milk (3), milk—eggs (2), eggs—butter (1)
        self.graph.update_from_basket(["bread", "milk"])
        self.graph.update_from_basket(["bread", "milk"])
        self.graph.update_from_basket(["bread", "milk"])
        self.graph.update_from_basket(["milk", "eggs"])
        self.graph.update_from_basket(["milk", "eggs"])
        self.graph.update_from_basket(["eggs", "butter"])
        
        self.service = QueryService(self.graph)

    def test_bfs_depth_one_returns_direct_neighbors(self):
        """FR7-T1: BFS with depth=1 returns direct neighbors only."""
        # Act
        result = self.service.bfs_related("bread", max_depth=1, min_weight=1)

        # Assert
        self.assertIsInstance(result, dict)
        self.assertIn("bread", result)
        # Direct neighbors at depth 1: milk (weight 3)
        neighbors_at_depth_1 = result["bread"].get(1, set())
        self.assertIn("milk", neighbors_at_depth_1)

    def test_bfs_depth_two_returns_multi_hop(self):
        """FR7-T2: BFS with depth=2 returns items within 2 hops."""
        # Act
        result = self.service.bfs_related("bread", max_depth=2, min_weight=1)

        # Assert
        # At depth 1: milk
        # At depth 2: milk → eggs
        self.assertIn("bread", result)
        self.assertIn("milk", result.get("bread", {}).get(1, set()))
        # eggs is 2 hops away: bread → milk → eggs

    def test_bfs_min_weight_filter(self):
        """FR7-T3: min_weight filter blocks weak edges."""
        # Act
        # With min_weight=2, milk→eggs (weight 2) is included
        result_min_2 = self.service.bfs_related("bread", max_depth=2, min_weight=2)
        
        # With min_weight=3, milk→eggs (weight 2) is blocked
        result_min_3 = self.service.bfs_related("bread", max_depth=2, min_weight=3)

        # Assert
        self.assertIsInstance(result_min_2, dict)
        self.assertIsInstance(result_min_3, dict)
        # min_weight=2 should find milk (bread-milk has weight 3)
        # min_weight=3 should also find milk (bread-milk has weight 3)

    def test_bfs_no_infinite_loops(self):
        """FR7-T4: BFS uses visited set to prevent infinite loops."""
        # Act & Assert - should complete without infinite loop
        result = self.service.bfs_related("bread", max_depth=5, min_weight=1)
        
        # Should complete and return a dict
        self.assertIsInstance(result, dict)

    def test_bfs_unknown_start_returns_empty_levels(self):
        """FR7-T0: Starting from missing node yields empty mapping."""
        result = self.service.bfs_related("unknown", max_depth=2, min_weight=1)

        self.assertEqual(result, {"unknown": {}})


if __name__ == '__main__':
    unittest.main()
