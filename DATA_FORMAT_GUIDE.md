# Data Format Guide for Phase 1 Implementation

## CSV Format

The input CSV file (`data/Supermarket_dataset_PAI.csv`) has the following structure:

```
Member_number,Date,itemDescription
1808,21-07-2015,tropical fruit
2552,05-01-2015,whole milk
2300,19-09-2015,pip fruit
1187,12-12-2015,other vegetables
3037,01-02-2015,whole milk
4941,14-02-2015,rolls/buns
...
```

### Columns

- **Member_number** (int): Customer identifier
- **Date** (str): Purchase date in format "DD-MM-YYYY"
- **itemDescription** (str): Product name / item description

---

## Basket Construction Logic

### Definition

A **basket** is the set of items purchased by a single customer (Member_number) on a single date (Date).

### Example

If the CSV contains:

```
1808,21-07-2015,tropical fruit
1808,21-07-2015,bread
1808,21-07-2015,milk
1808,22-07-2015,eggs
1808,22-07-2015,milk
2552,05-01-2015,whole milk
```

### Resulting Baskets

```
Basket 1: (1808, 21-07-2015) → ["bread", "milk", "tropical fruit"]  (sorted)
Basket 2: (1808, 22-07-2015) → ["eggs", "milk"]  (sorted)
Basket 3: (2552, 05-01-2015) → ["whole milk"]  (sorted)
```

---

## Processing Rules (For Phase 1 Tests)

### Rule 1: Group by (Member_number, Date)

All items with the same Member_number AND Date belong to one basket.

```python
key = (member_number, date)
# All rows with same key → one basket
```

### Rule 2: Deduplicate Items in Same Basket

If the same item appears multiple times in one basket (same Member_number + Date), keep only one copy.

**Example:**
```
1808,21-07-2015,bread
1808,21-07-2015,milk
1808,21-07-2015,bread  # duplicate!

Result basket: ["bread", "milk"]  (one "bread" only)
```

### Rule 3: Sort Items Alphabetically

Within each basket, sort item names alphabetically for determinism.

**Example:**
```
Items purchased: ["milk", "bread", "eggs"]
Sorted basket: ["bread", "eggs", "milk"]
```

### Rule 4: Filter Empty Items

If an item description is empty or None, skip it.

```python
if item and item.strip():  # Only non-empty items
    basket.append(item.strip())
```

### Rule 5: Trim Whitespace

Remove leading/trailing whitespace from item names.

```python
item = item.strip()
```

---

## Expected Output from TransactionLoader.load_from_csv()

### Return Type

`List[List[str]]` — a list of baskets, where each basket is a list of item names.

### Example Output

```python
[
    ["bread", "eggs", "milk"],           # Basket 1
    ["eggs", "milk"],                    # Basket 2
    ["whole milk"],                      # Basket 3
    ["butter", "rolls/buns"],            # Basket 4
    ...
]
```

### Invariants

1. Each basket is a list of strings
2. No basket contains duplicate items
3. Items within each basket are sorted alphabetically
4. No empty baskets
5. Order of baskets in output can be any (not sorted)

---

## Test Case Examples (For test_fr1_loader.py)

### Test 1: CSV Loads Without Error

```python
def test_load_csv_valid_file(self):
    """CSV file loads and returns list of lists."""
    loader = TransactionLoader()
    baskets = loader.load_from_csv("data/Supermarket_dataset_PAI.csv")
    
    # Should return a list
    self.assertIsInstance(baskets, list)
    
    # Each basket should be a list
    for basket in baskets:
        self.assertIsInstance(basket, list)
        for item in basket:
            self.assertIsInstance(item, str)
```

### Test 2: Grouping by (Member_number, Date)

```python
def test_grouping_by_member_and_date(self):
    """Items grouped by (Member_number, Date) produce correct baskets."""
    # Create minimal CSV content for testing
    csv_content = """Member_number,Date,itemDescription
1808,21-07-2015,bread
1808,21-07-2015,milk
1808,22-07-2015,eggs
2552,05-01-2015,whole milk
"""
    # Save to temp file, load, verify
    # Expected: 3 baskets
    #  - [bread, milk]
    #  - [eggs]
    #  - [whole milk]
```

### Test 3: Deduplication

```python
def test_deduplication_within_basket(self):
    """Duplicate items in same basket are removed."""
    csv_content = """Member_number,Date,itemDescription
1808,21-07-2015,bread
1808,21-07-2015,milk
1808,21-07-2015,bread
"""
    # Expected: 1 basket with ["bread", "milk"]
    # (bread appears only once despite being listed twice)
```

### Test 4: Sorting

```python
def test_alphabetical_sorting(self):
    """Items within baskets are sorted alphabetically."""
    csv_content = """Member_number,Date,itemDescription
1808,21-07-2015,milk
1808,21-07-2015,bread
1808,21-07-2015,eggs
"""
    # Expected: 1 basket with ["bread", "eggs", "milk"]
```

### Test 5: Empty Item Filtering

```python
def test_empty_items_filtered(self):
    """Empty/null item names are ignored."""
    csv_content = """Member_number,Date,itemDescription
1808,21-07-2015,bread
1808,21-07-2015,
1808,21-07-2015,milk
"""
    # Expected: 1 basket with ["bread", "milk"]
    # (empty item is skipped)
```

### Test 6: Whitespace Trimming

```python
def test_whitespace_trimmed(self):
    """Leading/trailing whitespace is removed from items."""
    csv_content = """Member_number,Date,itemDescription
1808,21-07-2015,  bread  
1808,21-07-2015,milk
"""
    # Expected: 1 basket with ["bread", "milk"]
    # (whitespace around "bread" is trimmed)
```

---

## Implementation Hints

### Approach 1: Using a Dictionary (Recommended)

```python
from collections import defaultdict

def load_from_csv(filepath):
    baskets_dict = defaultdict(set)  # (member, date) → set of items
    
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            member = row['Member_number']
            date = row['Date']
            item = row['itemDescription'].strip()
            
            if item:  # Skip empty items
                baskets_dict[(member, date)].add(item)  # set deduplicates
    
    # Convert to list of sorted baskets
    baskets = [sorted(list(items)) for items in baskets_dict.values()]
    return baskets
```

### Approach 2: Using a Nested Dictionary

```python
def load_from_csv(filepath):
    baskets_dict = {}  # {(member, date): set of items}
    
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row['Member_number'], row['Date'])
            item = row['itemDescription'].strip()
            
            if item:
                if key not in baskets_dict:
                    baskets_dict[key] = set()
                baskets_dict[key].add(item)
    
    # Convert to sorted lists
    baskets = [sorted(list(items)) for items in baskets_dict.values()]
    return baskets
```

### Key Points

1. Use **set** for deduplication (automatic)
2. **Sort** before returning (alphabetical order)
3. Use **DictReader** to handle CSV headers
4. **Trim whitespace** with `.strip()`
5. **Check for empty** items before adding
6. Return **list of lists** (not dict)

---

## Testing Approach (For test_fr1_loader.py)

### Use Temporary CSV Files

```python
import tempfile
import os

class TestTransactionLoader(unittest.TestCase):
    def test_example(self):
        # Create a temporary CSV file
        csv_content = """Member_number,Date,itemDescription
1808,21-07-2015,bread
1808,21-07-2015,milk
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            # Test the loader
            loader = TransactionLoader()
            baskets = loader.load_from_csv(temp_path)
            
            # Verify
            self.assertEqual(len(baskets), 1)
            self.assertEqual(baskets[0], ["bread", "milk"])
        finally:
            os.unlink(temp_path)  # Clean up
```

---

**Use this guide to write test cases and implement Phase 1!**
