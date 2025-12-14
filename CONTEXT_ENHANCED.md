# Market Basket Analysis Task 2: Complete Context & Design Document

## Overview

This document captures the **complete requirements, design decisions, and TDD implementation plan** for the Market Basket Analysis System assessment.

**Last Updated:** Dec 14, 2025  
**Status:** Phase 0 complete (scaffold), ready for Phase 1 (FR1 tests)

---

# 1) Full Context: What Task 2 Is and What You're Being Graded On

## 1.1 Scenario Context (Supermarket)

You have thousands of supermarket transactions ("market baskets").
Each transaction is the set/list of items purchased together by a customer during one shopping visit.

The supermarket wants you to efficiently answer:

- **Q1:** "Which items are most frequently bought together with bread?"
- **Q2:** "What are the top three most common product bundles across all transactions?"
- **Q3:** "How can we quickly identify whether two items are often co-purchased?"

## 1.2 What Task 2 Is Actually Assessing

Your grade is NOT for "finding clever patterns with ML." Your grade is for demonstrating:

1. **Correct data structure choice** (graph/tree/queue-based, etc.)
2. **Algorithms from your module operating on that structure** (sorting/ranking, searching/lookup, BFS/DFS traversal)
3. **An application extension** (visualisation/presentation + filters + recommendation-style query)
4. **Professional software engineering:**
   - Requirements (FR/NFR) clearly specified
   - OOP structure (SRP, encapsulation, composition)
   - TDD with automated tests (unittest)
   - Version control discipline (git with professional commits)
5. **Reflective report (750–1000 words):**
   - Justify your design choice
   - Complexity analysis (Big O notation)
   - Discuss alternatives considered and why rejected
   - Evaluate scalability

---

# 2) Task Requirements (What We Must Implement)

## 2.1 User Requirements (High-Level)

- Analysts can identify co-purchased products.
- Analysts can quickly check association strength between any two items.
- Analysts can run common queries easily.

## 2.2 System Requirements (Detailed)

### Functional Requirements (FRs)

We will implement and test:

- **FR1:** Ingest transaction data and represent each transaction as a basket (list of item names).
- **FR2:** Build co-occurrence counts for item pairs in the same basket.
- **FR3:** Retrieve co-purchase frequency for a given item pair.
- **FR4:** Return the **top K** most common bundles across all transactions (bundle = item pair).
- **FR5:** For a given item X (e.g., bread), return top items bought with X (ranked).
- **FR6:** Provide a "visualisation/presentation" that highlights the strongest associations.
- **FR7:** Provide filters for exploration (e.g., minimum frequency threshold, depth limit) and optionally BFS/DFS.
- **FR8:** Support updating the structure when new transactions arrive (incremental update, no full rebuild).

### Quantitative Non-Functional Requirements (NFRs)

These must be **measurable** (per module guidance on quantitative NFRs):

- **NFR1 (Lookup):** Pair-frequency lookup must complete in **< 50 ms**.
- **NFR2 (Build rate):** Initial build must process **≥ 1000 transactions/sec**.
- **NFR3 (Responsiveness):** Top-K output must display in **< 1 sec**.
- **NFR4 (Correctness):** 100% accuracy of co-occurrence counts (no missing/double counting).

---

# 3) Core Idea: Baskets to Relationship Network

Items that appear together in baskets become linked. We count how often each pair appears.

**Example baskets:**
```
[bread, milk, eggs]
[bread, milk]
[milk, cereal]
```

**Resulting co-occurrence counts:**
```
bread—milk: weight 2
bread—eggs: weight 1
milk—eggs: weight 1
milk—cereal: weight 1
```

---

# 4) Data Structure Choice: Weighted Undirected Graph (Adjacency List)

## 4.1 Why Graph (NOT Trees)?

**Original consideration:** Forest of customer trees (customer → date → items)

**Problems with trees:**
- Trees are hierarchical (parent→child), but co-purchases are peer-to-peer relationships
- Trees add implementation complexity without solving any required FR
- Would require extracting baskets from trees anyway, then building graph anyway—double work
- Per-customer analysis is NOT in scope for Task 2 rubric
- Makes design harder to justify in report

**Why pure graph is better:**
- Directly models pairwise relationships (edges = co-occurrences)
- All FRs (FR1–FR8) solved efficiently by single structure
- Clean, defensible design argument
- Faster implementation (fewer classes, fewer tests)
- Optimal complexity: O(1) lookup (Q3), O(E log E) ranking (Q2), O(deg) recommendation (Q1)

**Verdict:** Pure graph approach. No hybrid. Single, clean responsibility.

## 4.2 Representation: Nested Dictionaries (Adjacency List)

We store the graph as **nested dicts** (hash maps with average O(1) lookup):

```python
graph = {
    "bread": {
        "milk": 5,      # bread & milk co-purchased 5 times
        "eggs": 3,
    },
    "milk": {
        "bread": 5,     # symmetric (undirected)
        "eggs": 2,
    },
    "eggs": {
        "bread": 3,
        "milk": 2,
    },
    # ... more items
}
```

**Why this is perfect for queries:**

- **Q3 (pair check):** `graph["bread"].get("milk", 0)` → O(1) lookup
- **Q1 (items bought with bread):** `graph["bread"]` → neighbors sorted by weight → O(deg log deg)
- **Q2 (top bundles):** Extract unique edges, sort → O(E log E)

---

# 5) Algorithms We Will Use (Module-Aligned)

## 5.1 Graph Construction (FR2, FR8)

For each basket of size m:
- Generate all unordered pairs (i, j) with i < j
- Increment weight for each pair

**Complexity:**
- Pair generation per basket: O(m²) (nested loops)
- Increment: O(1) average per pair (dict lookup)
- Total build: Σ O(m²) over all transactions (discuss scalability in report)

## 5.2 FR3: Pair Frequency Lookup

```python
weight = graph[a].get(b, 0)
```

**Complexity:** O(1) average

## 5.3 FR5: "Bought with [item]" Recommendation

```python
neighbors = graph[item]
sorted_neighbors = sorted(neighbors.items(), key=lambda x: (-x[1], x[0]))
top_k = sorted_neighbors[:k]
```

**Complexity:** O(deg(item) log deg(item))

## 5.4 FR4: Top-K Bundles Globally

```python
# Extract unique edges only (avoid double-counting A-B and B-A)
edges = []
for a in graph:
    for b in graph[a]:
        if a < b:  # Only keep one direction
            edges.append((a, b, graph[a][b]))
# Sort by weight descending, then alphabetically
edges.sort(key=lambda x: (-x[2], x[0], x[1]))
top_k = edges[:k]
```

**Complexity:** O(E log E) where E = number of unique pairs

## 5.5 FR7: BFS/DFS Exploration (Optional but Recommended)

BFS using a queue (FIFO) to explore relationship layers:

```python
def bfs_related(start_item, max_depth, min_weight):
    # Returns all items within max_depth, connected via edges with weight >= min_weight
    # Complexity: O(V + E) on visited subgraph
    # Prevents cycles with visited set
```

---

# 6) Software Architecture (OOP, Testable)

We keep it simple and modular (fits testing guidance: separate files, test each unit).

## 6.1 Classes & Modules

### 1. TransactionLoader
- **File:** `src/transaction_loader.py`
- **Responsibility:** Read CSV, produce baskets
- **Methods:**
  - `load_from_csv(filepath) → List[List[str]]` returns list of baskets
  - Each basket is deduplicated and sorted
- **Handles:**
  - CSV parsing
  - Grouping by (Member_number, Date) or equivalent
  - Trimming whitespace
  - Removing duplicate items within basket
  - Sorting items deterministically

### 2. CooccurrenceGraph
- **File:** `src/cooccurrence_graph.py`
- **Responsibility:** Own the graph structure; provide updates and neighbor queries
- **Methods:**
  - `update_from_basket(basket: List[str]) → None` — increment pair weights
  - `get_weight(a: str, b: str) → int` — lookup pair frequency
  - `neighbors(item: str) → Dict[str, int]` — all items bought with item
  - `unique_edges() → List[Tuple[str, str, int]]` — all pairs (only a < b)

### 3. QueryService
- **File:** `src/query_service.py`
- **Responsibility:** Implement FR3–FR7 (queries on the graph)
- **Methods:**
  - `pair_frequency(a: str, b: str) → int` — alias for graph.get_weight()
  - `often_copurchased(a: str, b: str, threshold: int) → bool` — check >= threshold
  - `top_with_item(item: str, k: int) → List[Tuple[str, int]]` — FR5
  - `top_bundles(k: int) → List[Tuple[str, str, int]]` — FR4
  - `bfs_related(start: str, max_depth: int, min_weight: int) → Dict` — FR7 (optional)

### 4. Presenter
- **File:** `src/presenter.py`
- **Responsibility:** Format results for CLI output (FR6)
- **Methods:**
  - `format_top_bundles(bundles: List) → str` — pretty-print table
  - `format_recommendations(items: List, item_name: str) → str` — pretty-print recommendations
  - `format_pair(a: str, b: str, weight: int) → str` — single pair display

---

# 7) TDD Workflow (Commit Cadence)

You asked for: **write failing tests → commit failing tests → implement → commit passing code**

That is EXACTLY the workflow we will use.

### Global Rule for Each Feature

For every requirement chunk (each FR):

1. **Write tests first** (they fail because feature doesn't exist yet)
2. **Commit the failing tests**
   - Example: `test(FR2): add failing tests for basket pair updates`
3. Implement minimal production code until tests pass
4. **Commit passing code**
   - Example: `feat(FR2): implement graph update from basket`
5. Refactor if needed (tests still pass)
   - Example: Fold refactoring into previous commit (no separate refactor commit)

This is clean, professional, and matches the module's focus on automated testing and version control discipline.

---

# 8) Design Decisions (From Requirements Review, Dec 14, 2025)

### 8.1 Data Structure: Graph ✅ (NOT Trees)

**Decision:** Use single weighted undirected graph (adjacency list via nested dicts).

**Evidence:** Discussed above (Section 4.1). Trees rejected due to complexity without benefit.

### 8.2 User Interface: Text-Based CLI (NOT HTML/CSS)

**Decision:** Implement text-based CLI presentation (FR6) instead of HTML/CSS UI.

**Justification:**
- Assessment rubric does NOT require web interface
- Text output is simpler, faster to implement, easier to test
- Can still present data clearly (formatted tables, sorted lists, ASCII art)
- Aligns with professional CLI tool design (Unix philosophy)

**Implementation:** `Presenter` class with methods like `format_top_bundles()`, `format_recommendations()`, etc.

**Stretch goal (if time):** Add simple HTML dashboard later without changing core architecture.

### 8.3 Tie-Breaking Rule: Frequency Then Alphabetical

**Decision:** When two item pairs have equal weight:
1. Primary: Sort by **frequency (weight) descending**
2. Secondary: Sort **alphabetically** by item names (lexicographic)

**Example:**
```
If both (bread, eggs) and (bread, milk) have weight 5:
Sorted result: (bread, eggs) < (bread, milk)  [eggs < milk alphabetically]
```

**Why?**
- Reproducible across runs (deterministic)
- Simple to explain in report
- Easy to implement with Python's tuple sorting

### 8.4 Data Scope: Entire CSV

**Decision:** Use the **entire CSV dataset** (Supermarket_dataset_PAI.csv), not samples.

**Justification:**
- Real-world scale testing for NFRs (throughput, latency)
- Benchmark results will be meaningful
- No time wasted on sample creation/validation

### 8.5 Report Delivery: Separate .md File (Not Committed)

**Decision:** Create `REPORT_OUTLINE.md` as standalone scratch file (in `.gitignore`).

**Justification:**
- Outlines key sections (design, complexity, alternatives, scalability)
- User writes actual report later using these points as guide
- Keeps git history clean (no draft commits)
- Separates code deliverable (committed) from report deliverable (external)

### 8.6 No Self-Edges

**Decision:** Never create edges where both nodes are the same item.

**Implementation:** In `update_from_basket()`, skip pairs where `i == j`.

**Justification:** Self-loops are not meaningful; item bought with itself is implicit in single-item baskets.

### 8.7 CSV Format Assumptions

**Assumption:** CSV has columns like `Member_number`, `Date`, `itemDescription` (or similar).

**Basket Definition:**
- **Transaction:** One row in CSV (one purchase event)
- **Basket:** All items for unique (Member_number, Date) pair
- **Deduplication:** Remove duplicate items in same basket
- **Ordering:** Sort items within basket alphabetically (determinism)

**Validation:** Smoke test verifies CSV exists; FR1 tests verify parsing.

### 8.8 Performance Targets (Quantitative NFRs)

| ID | Requirement | Target | Justification |
|----|----|-----|----|
| NFR1 | Pair frequency lookup | < 50 ms | O(1) hash lookup |
| NFR2 | Transaction ingestion | ≥ 1000 tx/sec | Efficient basket extraction |
| NFR3 | Top-K query latency | < 1 sec | O(E log E) sorting |
| NFR4 | Accuracy | 100% | Exhaustive counting |

**Evidence:** Benchmark script (`benchmarks/run.py`) measures and reports these.

### 8.9 No External Dependencies

**Decision:** Use **only Python standard library** (no pandas, numpy, scipy, etc.).

**Justification:**
- Assessment is about DS & algorithms, not library usage
- Lighter dependencies = easier to test and grade
- stdlib suffices: `csv`, `collections`, `unittest`

### 8.10 Git Discipline: No Separate Refactor Commits

**Decision:** If refactoring improves code without changing behavior:
- Refactor locally
- Run tests (must pass)
- Do NOT create separate "refactor commit"
- Fold refactor into most recent feature commit

**Justification:** Keeps git history lean and feature-focused.

---

# 9) Phase-by-Phase TDD Plan

## Phase 0: Repository Scaffold ✅ (COMPLETE)

**Goal:** Project runs tests at all.

- [x] Initialize git repo
- [x] Create folders: `src/`, `tests/`, `benchmarks/`
- [x] Add `.gitignore`, `README.md`
- [x] Add smoke test (`tests/test_smoke.py`)
- [x] Verify tests pass

**Commit:** `chore: scaffold project structure with folders, gitignore, readme, and smoke test`

**Git status:** 1 commit

---

## Phase 1: FR1 Transaction Ingestion → Baskets (NEXT)

**Goal:** Convert CSV rows into baskets grouped by (Member_number, Date).

### Tests First (Write, Then Commit Failing)

File: `tests/test_fr1_loader.py`

- **FR1-T1:** CSV loads without error; returns list of lists
- **FR1-T2:** Transactions grouped by (Member_number, Date) produce correct baskets
- **FR1-T3:** Duplicate items in same basket removed
- **FR1-T4:** Empty/null item names ignored
- **FR1-T5:** Items within basket sorted alphabetically (deterministic)
- **FR1-T6:** Whitespace trimmed from item names

**Commit failing tests:**
```
test(FR1): add failing tests for transaction loading and basket construction

- Test CSV parsing without error
- Test (Member_number, Date) grouping
- Test item deduplication within basket
- Test empty item filtering
- Test deterministic alphabetical sorting
- Test whitespace trimming

All tests expected to fail (feature not yet implemented).
```

### Implementation (Make Tests Pass)

File: `src/transaction_loader.py`

Class: `TransactionLoader`

```python
class TransactionLoader:
    @staticmethod
    def load_from_csv(filepath: str) -> List[List[str]]:
        """
        Load CSV and return baskets.
        
        Args:
            filepath: Path to Supermarket_dataset_PAI.csv
            
        Returns:
            List of baskets, where each basket is a sorted list of unique item names.
        """
        # Implementation: parse CSV, group by (Member_number, Date), deduplicate, sort
```

**Commit passing code:**
```
feat(FR1): implement transaction loader to build baskets

- Implement TransactionLoader.load_from_csv(filepath)
- Parse CSV using csv module
- Group items by (Member_number, Date) as baskets
- Deduplicate items within each basket (set → list)
- Sort items alphabetically for determinism
- Trim whitespace from item names
- Skip empty/null items

All FR1 tests now pass. Ready for graph construction (Phase 2).
```

---

## Phase 2: FR2, FR8 Graph Build + Incremental Updates (NEXT AFTER PHASE 1)

**Goal:** Update edge weights correctly from baskets.

### Tests First

File: `tests/test_fr2_graph.py`

- **FR2-T1:** New graph returns 0 for unseen pair
- **FR2-T2:** Basket [A, B] increments both directions (symmetry check)
- **FR2-T3:** Basket [A, B, C] increments all 3 pairs (complete graph)
- **FR2-T4:** No self-edges (item paired with itself is skipped)
- **FR8-T1:** Second basket increments counts (incremental update)

**Commit failing tests:**
```
test(FR2, FR8): add failing tests for graph construction and updates

- Test unseen pair returns 0 weight
- Test bilateral edge increment (A-B and B-A)
- Test complete graph generation for 3-item basket
- Test no self-edges created
- Test incremental updates with multiple baskets

All tests expected to fail (feature not yet implemented).
```

### Implementation

File: `src/cooccurrence_graph.py`

Class: `CooccurrenceGraph`

```python
class CooccurrenceGraph:
    def __init__(self):
        self.graph = {}  # Dict[str, Dict[str, int]]
    
    def update_from_basket(self, basket: List[str]) -> None:
        """Update graph with co-occurrences from one basket."""
        # Generate pairs, increment weights
        
    def get_weight(self, a: str, b: str) -> int:
        """Get co-purchase frequency for pair (a, b)."""
        # O(1) lookup
        
    def neighbors(self, item: str) -> Dict[str, int]:
        """Get all items bought with item and their weights."""
        # Return graph[item] or empty dict if not found
        
    def unique_edges(self) -> List[Tuple[str, str, int]]:
        """Return all unique edges (only a < b to avoid duplicates)."""
        # Extract edges, ensuring uniqueness
```

**Commit passing code:**
```
feat(FR2, FR8): implement cooccurrence graph with incremental updates

- Implement CooccurrenceGraph class with adjacency list (nested dicts)
- Implement update_from_basket(basket) to generate pairs and increment weights
- Implement get_weight(a, b) for O(1) pair lookup
- Implement neighbors(item) to get co-purchase profile
- Implement unique_edges() to extract all pairs (only a < b)
- Ensure symmetry (A-B and B-A both incremented)
- Skip self-edges (i < j filtering)

All FR2 and FR8 tests now pass. Ready for queries (Phase 3).
```

---

## Phase 3: FR3 Pair Frequency Query

**Goal:** Fast lookup + "often co-purchased" boolean.

### Tests First

File: `tests/test_fr3_queries.py`

- **FR3-T1:** Missing pair returns 0
- **FR3-T2:** Known pair returns correct count
- **FR3-T3:** Threshold logic (weight >= threshold)

### Implementation

File: `src/query_service.py`

Class: `QueryService`

```python
class QueryService:
    def __init__(self, graph: CooccurrenceGraph):
        self.graph = graph
    
    def pair_frequency(self, a: str, b: str) -> int:
        """Get co-purchase frequency for pair (a, b)."""
        
    def often_copurchased(self, a: str, b: str, threshold: int) -> bool:
        """Check if pair (a, b) bought together >= threshold times."""
```

---

## Phase 4: FR5 "Bought with [Item]" Recommendations

**Goal:** Rank neighbors of an item by weight.

### Tests First

File: `tests/test_fr5_recommendations.py`

- **FR5-T1:** Results sorted by weight descending
- **FR5-T2:** Limit to K results
- **FR5-T3:** Missing item returns []
- **FR5-T4:** Tie-break: frequency then alphabetically

### Implementation

File: `src/query_service.py`

```python
class QueryService:
    def top_with_item(self, item: str, k: int) -> List[Tuple[str, int]]:
        """Return top K items bought with item, sorted by frequency."""
        neighbors = self.graph.neighbors(item)
        # Sort by weight desc, then alphabetically
        sorted_items = sorted(neighbors.items(), key=lambda x: (-x[1], x[0]))
        return sorted_items[:k]
```

---

## Phase 5: FR4 Top-K Bundles

**Goal:** Return global top pairs.

### Tests First

File: `tests/test_fr4_bundles.py`

- **FR4-T1:** Unique edges only (avoid A-B and B-A double-count)
- **FR4-T2:** Correct ordering
- **FR4-T3:** K > edges returns all
- **FR4-T4:** Tie-break deterministic

### Implementation

```python
class QueryService:
    def top_bundles(self, k: int) -> List[Tuple[str, str, int]]:
        """Return top K item pairs by co-purchase frequency."""
        edges = self.graph.unique_edges()
        # Sort by weight desc, then alphabetically
        edges.sort(key=lambda x: (-x[2], x[0], x[1]))
        return edges[:k]
```

---

## Phase 6: FR7 BFS/DFS Exploration

**Goal:** Explore relationships beyond direct neighbors.

### Tests First

File: `tests/test_fr7_exploration.py`

- **FR7-T1:** BFS depth=1 returns direct neighbors
- **FR7-T2:** BFS depth=2 returns second-hop nodes
- **FR7-T3:** min_weight filter blocks weak edges
- **FR7-T4:** No infinite loops (visited set)

### Implementation

```python
class QueryService:
    def bfs_related(self, start: str, max_depth: int, min_weight: int = 1) -> Dict:
        """Explore items related to start via BFS."""
        # BFS with queue, visited set, weight filtering
```

---

## Phase 7: FR6 CLI Presentation

**Goal:** Highlight strongest associations.

### Tests First

File: `tests/test_fr6_presenter.py` (or integrated into test_fr4, test_fr5)

- **FR6-T1:** Presenter returns formatted output
- **FR6-T2:** Respects min_weight threshold
- **FR6-T3:** Handles empty graph cleanly

### Implementation

File: `src/presenter.py`

```python
class Presenter:
    @staticmethod
    def format_top_bundles(bundles: List[Tuple[str, str, int]]) -> str:
        """Pretty-print top bundles as table."""
        
    @staticmethod
    def format_recommendations(items: List[Tuple[str, int]], item_name: str) -> str:
        """Pretty-print recommendations for item."""
```

---

## Phase 8: Benchmarks (NFR Evidence)

**Goal:** Measure, don't just claim.

File: `benchmarks/run.py`

```python
# Time build transactions/sec (NFR2)
# Time repeated pair lookup average (NFR1)
# Time top-K queries (NFR3)
# Verify accuracy (NFR4)
```

**Commit:**
```
chore: add benchmark suite for NFR measurements

- Measure transaction ingestion rate (NFR2: target >= 1000 tx/sec)
- Measure pair lookup latency (NFR1: target < 50 ms)
- Measure top-K query latency (NFR3: target < 1 sec)
- Verify accuracy (NFR4: 100% correctness)
- Output results to benchmarks/results.txt
```

---

## Phase 9: Documentation & Report Outline

**Goal:** Prepare evidence for report.

File: `REPORT_OUTLINE.md` (in `.gitignore`, not committed)

Sections to address:
1. Design Justification: Why graph + adjacency list?
2. Complexity Analysis: Build O(Σm²), lookup O(1), ranking O(E log E), BFS O(V+E)
3. Alternatives: List-of-pairs, matrix, Apriori algorithm (explain why out of scope)
4. Scalability: Larger data, dynamic updates, memory growth
5. Evidence: Benchmark numbers + test coverage

---

# 10) Deliverables Checklist

## Code Deliverables

- [x] `src/transaction_loader.py` (Phase 1)
- [ ] `src/cooccurrence_graph.py` (Phase 2)
- [ ] `src/query_service.py` (Phases 3–7)
- [ ] `src/presenter.py` (Phase 7)
- [ ] `tests/test_fr1_loader.py` through `test_fr7_exploration.py` (Phases 1–7)
- [ ] `benchmarks/run.py` (Phase 8)

## Documentation

- [x] `README.md` (Phase 0)
- [x] `.gitignore` (Phase 0)
- [ ] `REPORT_OUTLINE.md` (Phase 9, not committed)
- [ ] Reflective Report (750–1000 words) — Written by you later

## Git Commits (Target Count)

Expected ~20–25 commits following TDD cadence:
- 1 scaffold
- 2 per FR (failing tests → passing code)
- 1 benchmarks
- Total: ~18 feature commits

---

# 11) Key Principles (Recap)

1. **Pure Graph:** No trees, no hybrid structures. Single responsibility.
2. **TDD Discipline:** Write tests first, commit failing, implement, commit passing.
3. **Text CLI:** No HTML/CSS; clean stdout output.
4. **Determinism:** Tie-break by frequency, then alphabetically.
5. **No Dependencies:** stdlib only.
6. **Quantitative NFRs:** Benchmark and measure everything.
7. **Professional Git:** Clear messages (Summary/Why/What format).

---

**Ready for Phase 1?** Write failing tests for FR1 (transaction loading).
