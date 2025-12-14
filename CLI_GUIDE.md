# CLI User Guide

## Quick Start

```bash
python main.py
```

## Smart Item Matching

The CLI includes intelligent item matching to make searches easier:

### How It Works:

1. **Type any part of an item name**
   ```
   Enter item name: bread
   ```

2. **If matches found, get a numbered menu with aggregation option:**
   ```
   📋 Found 3 items matching 'bread':
   
     1. brown bread
     2. semi-finished bread
     3. white bread
     all. Show results for ALL items
     0. Cancel
   
   Select item number (or 'all'): 
   ```

3. **Choose an option:**
   - **Enter 1, 2, or 3:** See results for that specific item
   - **Type 'all':** Aggregate results across all matching items
   - **Enter 0 or 'cancel':** Cancel the operation

4. **Example with 'all' option:**
   ```
   Select item number (or 'all'): all
   How many top items? (default 10): 5
   ============================================================
   TOP 5 ITEMS BOUGHT WITH: BROWN BREAD, SEMI-FINISHED BREAD, WHITE BREAD
   ============================================================
   Rank   Item                           Co-Purchases
   ------------------------------------------------
   1      whole milk                     139
   2      other vegetables               100
   3      rolls/buns                     93
   ...
   ```

### Examples:

**Partial Search (gets menu):**
```
Enter item name: bread
→ Shows 3 options
→ User picks one
→ Continues with selection
```

**Exact Name:**
```
Enter item name: whole milk
→ Exact match found
→ Proceeds directly (no menu)
```

**No Matches:**
```
Enter item name: xyz
→ ❌ 'xyz' not found in dataset
```

## Features

### 1. **Find Items Bought With [ITEM]**
   - Search for the top N items most frequently co-purchased with a specific item
   - **Case-insensitive** - "whole milk", "WHOLE MILK", "Whole Milk" all work
   - **Smart matching:** Type partial names and get options to choose from
   - **NEW: Aggregation mode** - Select "all" to combine results across all matching items
   - Shows ranked results with co-purchase frequency
   - **Example 1:** Find top 5 items bought with "whole milk" (single item)
   - **Example 2:** Find top 5 items bought with ANY bread type (aggregated)

### 2. **Find Top Bundles**
   - See the most frequently co-purchased item pairs
   - Sorted by frequency (descending)
   - Useful for cross-selling and promotions
   - **Example:** Show top 20 bundles

### 3. **Check Co-Purchase Frequency**
   - Query specific pairs: "How many times were these two items bought together?"
   - **Case-insensitive matching** with suggestions for both items
   - **NEW: Multi-item aggregation** - Select "all" for both items to sum frequencies
   - Exact count returned
   - **Example 1:** Frequency of "bread" and "butter" (single pair)
   - **Example 2:** Total frequency of (ANY bread type) × (ANY milk type) (aggregated)

### 4. **Explore Related Items (BFS)**
   - Navigate the co-purchase network by depth
   - Control exploration depth (1, 2, 3, ...)
   - Filter by minimum co-purchase frequency
   - **NEW: Multi-item exploration** - Select "all" to explore network from all matching items
   - Shows items at each degree of separation
   - **Example 1:** Find items related to "milk" within 2 degrees (single start point)
   - **Example 2:** Find items related to ANY bread type within 2 degrees (aggregated)

### 5. **List Available Items**
   - View all 167 items in the dataset
   - Useful for finding exact item names
   - Alphabetically sorted
   - **Copy-paste ready for queries**

### 6. **Reload Dataset**
   - Re-read CSV and rebuild the graph
   - Useful for testing with updated data

## Logging

All CLI sessions are logged to `logs/cli_YYYYMMDD_HHMMSS.log`

**Logged Information:**
- Session start/end times
- Number of transactions loaded
- Graph size (items, edges)
- All user queries and their results
- Errors and warnings

## Example Queries

### Query 1: Top Items with Whole Milk
```
Select option: 1
Enter item name: whole milk
How many top items? (default 10): 5
```

### Query 2: Top 15 Bundles
```
Select option: 2
How many top bundles? (default 10): 15
```

### Query 3: Pair Frequency
```
Select option: 3
Enter first item: bread
Enter second item: butter
```

Result: "❌ No items found co-purchased..." (bread isn't in dataset)

Try instead: "white bread" and "butter"

### Query 4: BFS Exploration
```
Select option: 4
Enter item name: whole milk
Max exploration depth? (default 2): 2
Minimum co-purchase frequency? (default 1): 5
```

Shows items bought with milk (degree 1), and items bought with those (degree 2).

## Dataset Info

- **14,963 transactions** from supermarket
- **167 unique items**
- **6,260 unique item pairs** (edges in co-purchase graph)
- **Top bundle:** other vegetables + whole milk (222 co-purchases)

## Tips

1. **Don't know item names?** Use option 5 to list all items
2. **Fuzzy matching:** Search for "bread" → suggests "brown bread", "white bread"
3. **Check logs:** `tail -f logs/cli_*.log` to monitor activity
4. **Performance:** All queries complete in milliseconds (even on 14k transactions)

## Output Examples

### Top Bundles Output
```
============================================================
TOP PRODUCT BUNDLES (Item Pairs)
============================================================
Rank   Item 1               Item 2               Frequency
------------------------------------------------------------
1      other vegetables     whole milk           222     
2      rolls/buns           whole milk           209     
```

### Top Items Output
```
============================================================
TOP ITEMS BOUGHT WITH: WHOLE MILK
============================================================
Rank   Item                           Co-Purchases
------------------------------------------------------------
1      other vegetables               222     
2      rolls/buns                     209     
```

### BFS Output
```
📊 Items related to 'whole milk' (within 2 degrees, min frequency 5):

  Degree 1: other vegetables, rolls/buns, soda, yogurt
  Degree 2: butter, coffee, domestic eggs, other snacks, ...
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Item not found" | Use option 5 to find exact name, or try fuzzy match (e.g., "milk" instead of exact item) |
| Slow queries | Normal - graph has 6k edges, sorting is O(E log E) = ~80k ops = 20ms |
| No results for BFS | Increase max_depth or decrease min_weight threshold |
| Log file not found | Check `logs/` directory; created on first run |

---

**Enjoy exploring the supermarket co-purchase patterns!** 🛒📊
