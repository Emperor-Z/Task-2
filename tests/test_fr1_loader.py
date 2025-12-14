"""Unit tests for FR1: Transaction loading and basket construction.

Tests verify CSV parsing, grouping by (Member_number, Date), item deduplication,
filtering, whitespace trimming, and deterministic alphabetical sorting.

All tests are expected to fail initially (red → green workflow).
"""

import unittest
import tempfile
import os
from pathlib import Path


class TestTransactionLoader(unittest.TestCase):
    """Test cases for TransactionLoader class."""

    def setUp(self):
        """Set up temporary file storage for CSV tests."""
        self.temp_files = []

    def tearDown(self):
        """Clean up temporary files after each test."""
        for temp_path in self.temp_files:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def _write_csv(self, content: str) -> str:
        """Helper: Write CSV content to temp file and return path.
        
        Args:
            content: CSV file content as string
            
        Returns:
            Path to temporary CSV file
        """
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.csv', delete=False, newline=''
        ) as f:
            f.write(content)
            temp_path = f.name
        self.temp_files.append(temp_path)
        return temp_path

    def test_csv_loads_without_error(self):
        """FR1-T1: CSV file loads and returns list of lists."""
        # Arrange
        csv_content = """Member_number,Date,itemDescription
1808,21-07-2015,bread
1808,21-07-2015,milk"""
        csv_path = self._write_csv(csv_content)

        # Act
        from src.transaction_loader import TransactionLoader
        loader = TransactionLoader()
        baskets = loader.load_from_csv(csv_path)

        # Assert
        self.assertIsInstance(baskets, list)
        self.assertEqual(len(baskets), 1)
        self.assertIsInstance(baskets[0], list)
        for item in baskets[0]:
            self.assertIsInstance(item, str)

    def test_missing_file_raises_file_not_found(self):
        """FR1-T0: Missing CSV path raises FileNotFoundError."""
        from src.transaction_loader import TransactionLoader
        loader = TransactionLoader()

        with self.assertRaises(FileNotFoundError):
            loader.load_from_csv("does_not_exist.csv")

    def test_missing_required_columns_raise_value_error(self):
        """FR1-T0b: Missing required CSV columns raises ValueError."""
        csv_content = """Member_number,itemDescription
1808,bread"""
        csv_path = self._write_csv(csv_content)

        from src.transaction_loader import TransactionLoader
        loader = TransactionLoader()

        with self.assertRaises(ValueError):
            loader.load_from_csv(csv_path)

    def test_load_returns_list_of_baskets(self):
        """FR1-T1a: load_from_csv returns list of basket lists."""
        csv_content = """Member_number,Date,itemDescription
1808,21-07-2015,bread"""
        csv_path = self._write_csv(csv_content)

        from src.transaction_loader import TransactionLoader
        loader = TransactionLoader()

        baskets = loader.load_from_csv(csv_path)

        self.assertIsInstance(baskets, list)
        self.assertIsInstance(baskets[0], list)

    def test_grouping_by_member_and_date(self):
        """FR1-T2: Items grouped by (Member_number, Date) produce correct baskets."""
        # Arrange
        csv_content = """Member_number,Date,itemDescription
1808,21-07-2015,bread
1808,21-07-2015,milk
1808,22-07-2015,eggs
2552,05-01-2015,whole milk"""
        csv_path = self._write_csv(csv_content)

        # Act
        from src.transaction_loader import TransactionLoader
        loader = TransactionLoader()
        baskets = loader.load_from_csv(csv_path)

        # Assert
        self.assertEqual(len(baskets), 3, "Should have 3 baskets for 3 unique (member, date) pairs")
        
        # Each basket should be a list of items
        for basket in baskets:
            self.assertIsInstance(basket, list)
            for item in basket:
                self.assertIsInstance(item, str)

    def test_duplicate_items_removed_within_same_basket(self):
        """FR1-T3a: Loader removes duplicates inside a basket."""
        csv_content = """Member_number,Date,itemDescription
1808,21-07-2015,bread
1808,21-07-2015,bread
1808,21-07-2015,milk"""
        csv_path = self._write_csv(csv_content)

        from src.transaction_loader import TransactionLoader
        loader = TransactionLoader()
        baskets = loader.load_from_csv(csv_path)

        self.assertEqual(baskets[0].count("bread"), 1)

    def test_deduplication_within_basket(self):
        """FR1-T3: Duplicate items in same basket are removed."""
        # Arrange
        csv_content = """Member_number,Date,itemDescription
1808,21-07-2015,bread
1808,21-07-2015,milk
1808,21-07-2015,bread"""
        csv_path = self._write_csv(csv_content)

        # Act
        from src.transaction_loader import TransactionLoader
        loader = TransactionLoader()
        baskets = loader.load_from_csv(csv_path)

        # Assert
        self.assertEqual(len(baskets), 1)
        basket = baskets[0]
        # Bread should appear only once despite being listed twice
        self.assertEqual(basket.count("bread"), 1, "Duplicate items should be removed")
        self.assertIn("bread", basket)
        self.assertIn("milk", basket)
        self.assertEqual(len(basket), 2, "Basket should have 2 unique items")

    def test_empty_items_filtered(self):
        """FR1-T4: Empty/null item names are ignored."""
        # Arrange
        csv_content = """Member_number,Date,itemDescription
1808,21-07-2015,bread
1808,21-07-2015,
1808,21-07-2015,milk"""
        csv_path = self._write_csv(csv_content)

        # Act
        from src.transaction_loader import TransactionLoader
        loader = TransactionLoader()
        baskets = loader.load_from_csv(csv_path)

        # Assert
        self.assertEqual(len(baskets), 1)
        basket = baskets[0]
        self.assertEqual(len(basket), 2, "Empty items should be filtered out")
        self.assertIn("bread", basket)
        self.assertIn("milk", basket)
        self.assertNotIn("", basket)

    def test_empty_after_strip_is_filtered(self):
        """FR1-T4a: Items with whitespace-only names are dropped."""
        csv_content = """Member_number,Date,itemDescription
1808,21-07-2015,   
1808,21-07-2015,bread"""
        csv_path = self._write_csv(csv_content)

        from src.transaction_loader import TransactionLoader
        loader = TransactionLoader()
        baskets = loader.load_from_csv(csv_path)

        self.assertEqual(len(baskets[0]), 1)
        self.assertEqual(baskets[0][0], "bread")

    def test_alphabetical_sorting(self):
        """FR1-T5: Items within baskets are sorted alphabetically (deterministic)."""
        # Arrange
        csv_content = """Member_number,Date,itemDescription
1808,21-07-2015,milk
1808,21-07-2015,bread
1808,21-07-2015,eggs"""
        csv_path = self._write_csv(csv_content)

        # Act
        from src.transaction_loader import TransactionLoader
        loader = TransactionLoader()
        baskets = loader.load_from_csv(csv_path)

        # Assert
        self.assertEqual(len(baskets), 1)
        basket = baskets[0]
        expected = ["bread", "eggs", "milk"]
        self.assertEqual(basket, expected, "Items must be sorted alphabetically")

    def test_items_sorted_even_if_inserted_unsorted(self):
        """FR1-T5a: Sorting applied regardless of input order."""
        csv_content = """Member_number,Date,itemDescription
1808,21-07-2015,zebra
1808,21-07-2015,apple"""
        csv_path = self._write_csv(csv_content)

        from src.transaction_loader import TransactionLoader
        loader = TransactionLoader()
        baskets = loader.load_from_csv(csv_path)

        self.assertEqual(baskets[0], ["apple", "zebra"])

    def test_whitespace_trimmed(self):
        """FR1-T6: Leading/trailing whitespace is removed from item names."""
        # Arrange
        csv_content = """Member_number,Date,itemDescription
1808,21-07-2015,  bread  
1808,21-07-2015,milk
1808,21-07-2015,  eggs"""
        csv_path = self._write_csv(csv_content)

        # Act
        from src.transaction_loader import TransactionLoader
        loader = TransactionLoader()
        baskets = loader.load_from_csv(csv_path)

        # Assert
        self.assertEqual(len(baskets), 1)
        basket = baskets[0]
        expected = ["bread", "eggs", "milk"]
        self.assertEqual(basket, expected, "Whitespace should be trimmed from items")
        # Verify no item has leading/trailing spaces
        for item in basket:
            self.assertEqual(item, item.strip(), f"Item '{item}' has untracked whitespace")


if __name__ == '__main__':
    unittest.main()
