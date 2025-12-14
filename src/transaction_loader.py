"""FR1: Transaction loading and basket construction.

Ingests supermarket transaction CSV and constructs baskets (item sets)
grouped by (Member_number, Date) with deduplication and sorting.
"""

import csv
import os
from typing import List
from collections import defaultdict


class TransactionLoader:
    """Load and process supermarket transaction CSV into baskets.
    
    A basket is the set of items purchased by a customer on a single date.
    Each unique (Member_number, Date) pair produces one basket.
    """

    @staticmethod
    def load_from_csv(filepath: str) -> List[List[str]]:
        """Load CSV and return list of baskets (deduplicated, sorted).
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"CSV file not found: {filepath}")

        return []
