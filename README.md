# Market Basket Analysis System

A Python-based data structure and algorithm solution for analyzing customer purchasing patterns from supermarket transaction records.

## Overview

This project implements an efficient market basket analysis system to answer key business questions:

- **Q1:** "Which items are most frequently bought together with bread?"
- **Q2:** "What are the top three most common product bundles across all transactions?"
- **Q3:** "How can we quickly identify whether two items are often co-purchased?"

## Project Structure

```
├── src/                           # Production code
│   ├── __init__.py
│   ├── transaction_loader.py      # FR1: Data ingestion & basket construction
│   ├── cooccurrence_graph.py      # FR2, FR8: Graph construction & updates
│   ├── query_service.py           # FR3-FR7: Query operations & recommendations
│   └── presenter.py               # FR6: CLI presentation
├── tests/                         # Unit tests (unittest framework)
│   ├── __init__.py
│   ├── test_smoke.py              # Framework verification
│   ├── test_fr1_loader.py         # FR1: Data loading tests
│   ├── test_fr2_graph.py          # FR2, FR8: Graph construction tests
│   ├── test_fr3_queries.py        # FR3: Pair frequency lookup tests
│   ├── test_fr4_bundles.py        # FR4: Top-K bundles tests
│   ├── test_fr5_recommendations.py # FR5: Top-with-item tests
│   └── test_fr7_exploration.py    # FR7: BFS exploration tests
├── data/                          # Input data
│   └── Supermarket_dataset_PAI.csv
├── benchmarks/                    # Performance measurements
│   └── run.py
├── .gitignore
├── README.md
└── context.md
```

## Running Tests

```bash
# Run all tests with verbose output
python -m unittest discover tests/ -v

# Run specific test file
python -m unittest tests.test_fr1_loader -v

# Run specific test case
python -m unittest tests.test_fr1_loader.TestTransactionLoader.test_load_csv_valid_file -v
```

## Data Structure

**Weighted Undirected Graph (Adjacency List via Nested Dicts)**

Representation:
```python
graph = {
    "bread": {
        "milk": 5,      # bread & milk co-purchased 5 times
        "eggs": 3,
    },
    "milk": {
        "bread": 5,     # symmetric (undirected)
        "butter": 2,
    },
    # ... more items
}
```

**Why this structure:**
- O(1) average lookup time for pair frequency (hash maps)
- O(deg) for finding all items bought with a specific item
- O(E log E) for ranking all pairs
- Efficient incremental updates
- Memory efficient for sparse graphs

## Requirements

- Python 3.9+
- No external dependencies (uses only Python stdlib)

## Design Principles

### Data Structures & Algorithms
- **Graph (Adjacency List):** Optimal O(1) lookup for pair queries
- **Sorting:** O(n log n) for ranking bundles and recommendations
- **BFS Traversal:** O(V+E) for multi-hop relationship exploration
- **Hashing:** O(1) average for basket deduplication and lookups

### Software Engineering
- **SOLID Principles:** Single Responsibility, Composition over Inheritance
- **TDD Workflow:** Write failing tests → implement → pass → refactor
- **PEP 8 Compliance:** snake_case variables, PascalCase classes
- **Error Handling:** Meaningful exceptions, validation of inputs
- **Professional Git:** Clear commit messages (Summary/Why/What format)

## TDD Workflow

Each phase follows:
1. Write failing tests (test → commit)
2. Implement production code (code → commit)
3. Refactor if needed (tests still pass)

## Performance Targets (NFRs)

| Requirement | Target | Justification |
|-------------|--------|---------------|
| NFR1: Pair lookup latency | < 50 ms | O(1) hash table access |
| NFR2: Transaction ingestion | ≥ 1000 tx/sec | Efficient basket extraction |
| NFR3: Top-K query latency | < 1 sec | O(E log E) sorting |
| NFR4: Accuracy | 100% | Exhaustive pair counting |

## Implementation Phases

- **Phase 0:** Repository scaffold ✅
- **Phase 1:** FR1 (Transaction loading)
- **Phase 2:** FR2, FR8 (Graph construction)
- **Phase 3:** FR3 (Pair lookup)
- **Phase 4:** FR5 (Top-with-item recommendations)
- **Phase 5:** FR4 (Top-K bundles)
- **Phase 6:** FR7 (BFS exploration) - optional
- **Phase 7:** FR6 (CLI presentation)
- **Phase 8:** Benchmarks & NFR verification
- **Phase 9:** Report & documentation

## Usage Example (Post-Implementation)

```bash
# Interactive CLI (recommended)
python main.py

# Run automated benchmarks
python benchmarks/run.py

# Run all unit tests
python -m unittest discover tests/ -v
```

## Interactive CLI

The system includes a user-friendly command-line interface:

```bash
$ python main.py
======================================================================
MARKET BASKET ANALYSIS - INTERACTIVE CLI
======================================================================

--- MAIN MENU ---
1. Find items bought with [ITEM]
2. Find top bundles (most frequently co-purchased pairs)
3. Check co-purchase frequency between two items
4. Explore related items (BFS)
5. List available items
6. Load new dataset (reload CSV)
0. Exit

Select option: 2
How many top bundles? (default 10): 10

============================================================
TOP PRODUCT BUNDLES (Item Pairs)
============================================================
Rank   Item 1               Item 2               Frequency
------------------------------------------------------------
1      other vegetables     whole milk           222     
2      rolls/buns           whole milk           209     
3      soda                 whole milk           174     
...
```

**Features:**
- ✅ Case-insensitive search (fuzzy matching)
- ✅ Full session logging to `logs/cli_YYYYMMDD_HHMMSS.log`
- ✅ Helpful error messages and suggestions
- ✅ ASCII table formatting for readability

See `CLI_GUIDE.md` for detailed usage examples.

## Key Features

### 1. **Data Loading (FR1)**
- Parse CSV files with customer transactions
- Group items by (Member_number, Date)
- Automatic deduplication and alphabetical sorting
- Handles missing columns gracefully

### 2. **Graph Construction (FR2, FR8)**
- Weighted undirected graph using adjacency list
- O(1) pair lookup: `graph[item1][item2]` → frequency
- Incremental updates: add new baskets to existing graph
- No self-edges: filters pairs with (i < j)

### 3. **Query Operations (FR3-FR5)**
- **Pair Frequency (FR3):** Look up how often two items bought together
- **Top Bundles (FR4):** Rank item pairs by co-purchase frequency
- **Top Recommendations (FR5):** Find items most often bought with a specific item
- **Deterministic sorting:** Tie-breaking with (-frequency, item_name)

### 4. **Network Exploration (FR7)**
- BFS (breadth-first search) for related item discovery
- Control depth of exploration (1, 2, 3, ... degrees)
- Filter by minimum co-purchase frequency
- Shows items at each distance level

### 5. **Text Presentation (FR6)**
- ASCII table formatting for console output
- Ranked results with frequency counts
- Easy-to-read column alignment
- No external dependencies (pure stdlib)

## Architecture

```
┌─────────────────────────────────────────────────────┐
│ CSV File (data/)                                    │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ TransactionLoader (FR1)                              │
│ - load_from_csv()                                    │
│ - Returns: List[List[items]]                         │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ CooccurrenceGraph (FR2, FR8)                         │
│ - update_from_basket()                              │
│ - get_weight()                                       │
│ - neighbors()                                        │
│ - unique_edges()                                     │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ QueryService (FR3-FR7)                              │
│ - pair_frequency()                                   │
│ - top_bundles()                                      │
│ - top_with_item()                                    │
│ - bfs_related()                                      │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ Presenter (FR6)                                      │
│ - format_top_bundles()                              │
│ - format_recommendations()                          │
│ - format_pair()                                      │
└─────────────────────────────────────────────────────┘
```

## Performance (NFRs)

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| **NFR1: Pair Lookup** | < 50 ms | 0.000088 ms | ✅ 537k× faster |
| **NFR2: Ingestion Rate** | ≥ 1,000 tx/sec | 212,529 tx/sec | ✅ 212× faster |
| **NFR3: Top-K Query** | < 1 sec | 0.023 sec | ✅ 43× faster |
| **NFR4: Accuracy** | ✓ | 100% (34/34 tests) | ✅ Verified |

### Complexity Analysis

- **CSV Loading:** O(n) where n = number of transactions
- **Graph Construction:** O(Σm²) where m = avg basket size (typically O(n))
- **Pair Lookup:** O(1) via dict access
- **Top-K Ranking:** O(E log E) where E = number of edges
- **BFS Exploration:** O(V + E) with depth/weight filtering

## Test Coverage

- **34 unit tests** across 5 test files
- **Framework:** Python unittest (built-in)
- **Coverage:** All features (FR1-FR8)
- **Edge cases:** Empty graphs, missing items, self-edges, ties
- **Execution time:** 6 milliseconds

Run tests:
```bash
python -m unittest discover tests/ -v
```

## Dataset

**File:** `data/Supermarket_dataset_PAI.csv`

| Metric | Value |
|--------|-------|
| Transactions | 14,963 |
| Unique Items | 167 |
| Item Pairs | 6,260 |
| Top Bundle | other vegetables + whole milk (222) |

## Dependencies

**None** — Uses Python stdlib only:
- `csv` — CSV parsing
- `collections` — defaultdict, deque
- `unittest` — Testing framework
- `time` — Performance benchmarking

## Documentation

- **README.md** — This file (overview & quick start)
- **CLI_GUIDE.md** — Interactive CLI usage examples


## Git History

15 atomic commits showing development process:

```
d8e6745 - docs: add CLI guide and update gitignore
8a8db0a - feat(CLI): add interactive CLI with logging
ed87ecf - chore: add comprehensive benchmark suite
36381ec - refactor: fix FR6/FR7 tests to match output
ae98cb4 - feat(FR6, FR7): implement presenter and BFS
... [9 more implementation commits]
05239c3 - chore: scaffold project structure
```

View with: `git log --oneline`

---

**Author:** PAI Assessment Task 2  
**Date:** December 2025  
**Status:** ✅ Complete — Ready for report writing

