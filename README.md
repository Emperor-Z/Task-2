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
python src/app.py --top-bundles 10
python src/app.py --top-with-item bread 5
python src/app.py --pair-frequency bread milk
```

---

**Author:** [Your Name]  
**Date:** December 2025  
**Assessment:** PAI Task 2 — Market Basket Analysis
