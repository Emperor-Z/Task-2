"""FR1: Transaction loading and basket construction.

Ingests supermarket transaction CSV and constructs baskets (item sets)
grouped by (Member_number, Date) with deduplication and sorting.
"""

import csv
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
        
        Each basket is a list of unique item names, sorted alphabetically.
        Items are grouped by (Member_number, Date) from the CSV.
        
        Args:
            filepath: Path to CSV file with columns:
                      Member_number, Date, itemDescription
        
        Returns:
            List of baskets, where each basket is a sorted list of item names.
            Order of baskets in list is arbitrary.
        
        Processing:
            1. Group items by (Member_number, Date) key
            2. Use set to automatically deduplicate items
            3. Sort items alphabetically for determinism
            4. Filter out empty/null items
            5. Trim whitespace from all items
        """
        # Dictionary to collect items for each (member, date) pair
        baskets_dict = defaultdict(set)
        
        try:
            with open(filepath, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    member_number = row['Member_number']
                    date = row['Date']
                    item = row['itemDescription'].strip()
                    
                    # Skip empty items
                    if item:
                        # Create (member, date) key
                        key = (member_number, date)
                        # Add item to set (automatically deduplicates)
                        baskets_dict[key].add(item)
        
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {filepath}")
        except KeyError as e:
            raise ValueError(f"CSV missing required column: {e}")
        
        # Convert sets to sorted lists
        baskets = [
            sorted(list(items))
            for items in baskets_dict.values()
        ]
        
        return baskets
