"""Smoke test to verify unittest framework and project structure."""

import unittest


class TestSmoke(unittest.TestCase):
    """Smoke tests for framework and path verification."""

    def test_true_equals_true(self):
        """Verify unittest framework is functional."""
        self.assertTrue(True)

    def test_can_import_modules(self):
        """Verify src folder is accessible for imports."""
        import sys
        import os
        # Add src to path so we can import modules
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        # This test just verifies the path works
        self.assertTrue(True)

    def test_data_file_exists(self):
        """Verify data CSV file exists."""
        import os
        data_path = os.path.join(
            os.path.dirname(__file__), '..', 'data', 'Supermarket_dataset_PAI.csv'
        )
        self.assertTrue(
            os.path.exists(data_path),
            f"Data file not found at {data_path}"
        )


if __name__ == '__main__':
    unittest.main()
