# Market Basket Analysis — Master Implementation Checklist

## Phase 0 ✅ COMPLETE

**Status:** Ready for Phase 1

### Completed (Dec 14, 2025)

- [x] Initialize git repository
- [x] Create folder structure (src/, tests/, benchmarks/)
- [x] Create .gitignore with Python/IDE/test excludes
- [x] Create README.md with project overview and design principles
- [x] Create src/__init__.py and tests/__init__.py
- [x] Create smoke test (test_smoke.py) — 3 tests passing
- [x] Create CONTEXT_ENHANCED.md — complete design document
- [x] Create PHASE_0_SUMMARY.md — quick reference guide
- [x] Create DATA_FORMAT_GUIDE.md — Phase 1 implementation guide
- [x] Make 2 git commits with professional messages
- [x] Verify all smoke tests pass (3/3)

**Git commits:** 2  
**Tests passing:** 3/3  

---

## Phase 1: FR1 Transaction Loading (NEXT)

**Goal:** Load CSV, group by (Member_number, Date), produce baskets

### TODO: Tests First

- [ ] Create `tests/test_fr1_loader.py`
- [ ] Write 6 failing test cases:
  - [ ] T1: CSV loads without error
  - [ ] T2: Grouping by (Member_number, Date) correct
  - [ ] T3: Deduplication within basket
  - [ ] T4: Empty items filtered
  - [ ] T5: Deterministic sorting (alphabetical)
  - [ ] T6: Whitespace trimming
- [ ] Run tests (all should fail)
- [ ] **Commit:** `test(FR1): add failing tests for transaction loading and basket construction`

**Reference:** See `DATA_FORMAT_GUIDE.md` for examples

### TODO: Implementation

- [ ] Create `src/transaction_loader.py`
- [ ] Implement `TransactionLoader` class
- [ ] Implement `load_from_csv(filepath: str) → List[List[str]]`
  - [ ] Parse CSV using csv module
  - [ ] Group items by (Member_number, Date)
  - [ ] Deduplicate items (use set)
  - [ ] Sort items alphabetically
  - [ ] Trim whitespace
  - [ ] Skip empty items
- [ ] Run tests (all should pass)
- [ ] **Commit:** `feat(FR1): implement transaction loader to build baskets`

**Expected result:** All 6 FR1 tests passing + 3 smoke tests = 9/9 ✅

---

## Phase 2: FR2, FR8 Graph Construction & Updates

**Goal:** Build weighted undirected graph, support incremental updates

### TODO: Tests First

- [ ] Create `tests/test_fr2_graph.py`
- [ ] Write 5 failing test cases:
  - [ ] T1: New graph returns 0 for unseen pair
  - [ ] T2: Basket [A,B] increments both directions (symmetry)
  - [ ] T3: Basket [A,B,C] increments all 3 pairs
  - [ ] T4: No self-edges (i == j skipped)
  - [ ] T5: Incremental updates work (second basket)
- [ ] Run tests (all should fail)
- [ ] **Commit:** `test(FR2, FR8): add failing tests for graph construction and incremental updates`

### TODO: Implementation

- [ ] Create `src/cooccurrence_graph.py`
- [ ] Implement `CooccurrenceGraph` class
  - [ ] `__init__()` initializes empty graph dict
  - [ ] `update_from_basket(basket)` — generates pairs, increments weights
  - [ ] `get_weight(a, b) → int` — O(1) lookup
  - [ ] `neighbors(item) → Dict[str, int]` — all co-purchasers
  - [ ] `unique_edges() → List[Tuple[str, str, int]]` — all pairs (a < b)
- [ ] Ensure symmetry (A-B and B-A both updated)
- [ ] Skip self-edges (i < j in pair generation)
- [ ] Run tests (all should pass)
- [ ] **Commit:** `feat(FR2, FR8): implement cooccurrence graph with incremental updates`

**Expected result:** 5 FR2 tests + 6 FR1 tests + 3 smoke = 14/14 ✅

---

## Phase 3: FR3 Pair Frequency Query

**Goal:** Fast lookup of pair weights and co-purchase threshold check

### TODO: Tests First

- [ ] Create `tests/test_fr3_queries.py`
- [ ] Write 3 failing test cases:
  - [ ] T1: Missing pair returns 0
  - [ ] T2: Known pair returns correct count
  - [ ] T3: Threshold check (weight >= threshold)
- [ ] **Commit:** `test(FR3): add failing tests for pair frequency and threshold check`

### TODO: Implementation

- [ ] Create `src/query_service.py`
- [ ] Implement `QueryService` class
  - [ ] `__init__(graph: CooccurrenceGraph)` stores graph reference
  - [ ] `pair_frequency(a, b) → int` — calls graph.get_weight()
  - [ ] `often_copurchased(a, b, threshold) → bool` — checks weight >= threshold
- [ ] Run tests (all should pass)
- [ ] **Commit:** `feat(FR3): implement pair frequency lookup and co-purchase check`

**Expected result:** 3 FR3 tests + 14 previous = 17/17 ✅

---

## Phase 4: FR5 Top-with-Item Recommendations

**Goal:** For item X, return top K items bought with X

### TODO: Tests First

- [ ] Create `tests/test_fr5_recommendations.py` (or extend test_fr3_queries.py)
- [ ] Write 4 failing test cases:
  - [ ] T1: Results sorted by weight descending
  - [ ] T2: Limit to K results
  - [ ] T3: Missing item returns []
  - [ ] T4: Tie-break: frequency (desc), then alphabetically
- [ ] **Commit:** `test(FR5): add failing tests for top-with-item ranking`

### TODO: Implementation

- [ ] Add to `src/query_service.py`
  - [ ] `top_with_item(item, k) → List[Tuple[str, int]]`
  - [ ] Get neighbors from graph
  - [ ] Sort by weight desc, then alphabetically
  - [ ] Return top K
- [ ] Run tests (all should pass)
- [ ] **Commit:** `feat(FR5): implement top-with-item recommendation query`

**Expected result:** 4 FR5 tests + 17 previous = 21/21 ✅

---

## Phase 5: FR4 Top-K Bundles

**Goal:** Return global top K item pairs

### TODO: Tests First

- [ ] Create `tests/test_fr4_bundles.py`
- [ ] Write 4 failing test cases:
  - [ ] T1: Unique edges only (avoid A-B and B-A double-count)
  - [ ] T2: Correct ordering (weight desc, then alphabetically)
  - [ ] T3: K > edge_count returns all
  - [ ] T4: Tie-break deterministic
- [ ] **Commit:** `test(FR4): add failing tests for top-k bundles`

### TODO: Implementation

- [ ] Add to `src/query_service.py`
  - [ ] `top_bundles(k) → List[Tuple[str, str, int]]`
  - [ ] Call graph.unique_edges()
  - [ ] Sort by weight desc, then alphabetically (a, b)
  - [ ] Return top K
- [ ] Run tests (all should pass)
- [ ] **Commit:** `feat(FR4): implement top-k bundles ranking`

**Expected result:** 4 FR4 tests + 21 previous = 25/25 ✅

---

## Phase 6: FR7 BFS Exploration (Optional but Recommended)

**Goal:** Explore items related to start item via BFS with filters

### TODO: Tests First

- [ ] Create `tests/test_fr7_exploration.py`
- [ ] Write 4 failing test cases:
  - [ ] T1: BFS depth=1 returns direct neighbors
  - [ ] T2: BFS depth=2 returns second-hop items
  - [ ] T3: min_weight filter blocks weak edges
  - [ ] T4: No infinite loops (visited set)
- [ ] **Commit:** `test(FR7): add failing tests for BFS exploration with filters`

### TODO: Implementation

- [ ] Add to `src/query_service.py`
  - [ ] `bfs_related(start, max_depth, min_weight) → Dict`
  - [ ] Use collections.deque for BFS queue
  - [ ] Track visited nodes
  - [ ] Apply weight filter
  - [ ] Respect depth limit
- [ ] Run tests (all should pass)
- [ ] **Commit:** `feat(FR7): implement BFS relationship exploration with filters`

**Expected result:** 4 FR7 tests + 25 previous = 29/29 ✅

---

## Phase 7: FR6 CLI Presentation

**Goal:** Format and display results in text format

### TODO: Tests First

- [ ] Create `tests/test_fr6_presenter.py`
- [ ] Write 3 failing test cases:
  - [ ] T1: Format top bundles as readable output
  - [ ] T2: Format recommendations list
  - [ ] T3: Handle empty results gracefully
- [ ] **Commit:** `test(FR6): add failing tests for result presentation`

### TODO: Implementation

- [ ] Create `src/presenter.py`
- [ ] Implement `Presenter` class (static methods)
  - [ ] `format_top_bundles(bundles, top_n=10) → str`
  - [ ] `format_recommendations(items, item_name, top_k=5) → str`
  - [ ] `format_pair(a, b, weight) → str`
- [ ] Create attractive text-based output (aligned columns, clear labels)
- [ ] Run tests (all should pass)
- [ ] **Commit:** `feat(FR6): implement text-based CLI presentation of results`

**Expected result:** 3 FR6 tests + 29 previous = 32/32 ✅

---

## Phase 8: Benchmarks & NFR Verification

**Goal:** Measure performance against NFRs

### TODO: Benchmark Script

- [ ] Create `benchmarks/run.py`
- [ ] Implement benchmarks for:
  - [ ] **NFR2:** Transaction ingestion rate (target ≥ 1000 tx/sec)
  - [ ] **NFR1:** Pair lookup latency (target < 50 ms)
  - [ ] **NFR3:** Top-K query latency (target < 1 sec)
  - [ ] **NFR4:** Accuracy verification (100% correctness check)
- [ ] Capture results to `benchmarks/results.txt`
- [ ] **Commit:** `chore: add benchmark suite for NFR measurements`

**Expected result:** Benchmark data collected for report

---

## Phase 9: Report Outline & Documentation

**Goal:** Prepare structure for reflective report

### TODO: Report Outline

- [ ] Create `REPORT_OUTLINE.md` (in .gitignore, not committed)
- [ ] Include sections:
  1. **Design Justification:** Why graph + adjacency list? Why not alternatives?
  2. **Complexity Analysis:** Build O(Σm²), lookup O(1), ranking O(E log E), BFS O(V+E)
  3. **Alternatives Considered:** List-of-pairs, matrix, Apriori algorithm
  4. **Scalability Discussion:** Larger datasets, dynamic updates, memory growth
  5. **Evidence:** Benchmark numbers + test coverage statistics
  6. **References:** Module concepts, SOLID principles, OOP patterns

### TODO: Final Cleanup

- [ ] Verify all tests pass: `python -m unittest discover tests/ -v`
- [ ] Check code coverage (optional but good to know)
- [ ] Review all docstrings
- [ ] Final git log looks clean
- [ ] **Final commit:** `chore: final cleanup and integration`

**NOT committed to git (in .gitignore):**
- REPORT_OUTLINE.md (user writes actual report)

---

## Final Verification Checklist

### Code Quality
- [ ] All 32+ tests passing
- [ ] PEP 8 compliant (snake_case, PascalCase for classes)
- [ ] Type hints present (parameter types, return types)
- [ ] Docstrings on all public methods
- [ ] No unused imports
- [ ] Error handling appropriate (no silent failures)

### Architecture
- [ ] SRP: Each class has one responsibility
- [ ] Composition used (QueryService uses CooccurrenceGraph)
- [ ] No circular dependencies
- [ ] Encapsulation: Private attributes with public methods

### Testing
- [ ] All tests in unittest framework
- [ ] Edge cases covered (empty, missing items, etc.)
- [ ] Test names descriptive (test_what_should_happen)
- [ ] Setup/teardown as needed (temp files cleaned)

### Git History
- [ ] Professional commit messages (Summary/Why/What)
- [ ] ~20–25 commits total (1 scaffold + 18 feature pairs + 1 benchmarks + 1 final)
- [ ] Each commit atomic (one logical change)
- [ ] No "WIP" or "fixup" commits in final history

### Documentation
- [ ] README.md complete and accurate
- [ ] CONTEXT_ENHANCED.md fully detailed
- [ ] DATA_FORMAT_GUIDE.md helpful for Phase 1
- [ ] Code comments explain why, not what
- [ ] Report outline provided (not committed)

### Performance
- [ ] NFR1: Pair lookup < 50 ms ✓
- [ ] NFR2: Build rate ≥ 1000 tx/sec ✓
- [ ] NFR3: Top-K queries < 1 sec ✓
- [ ] NFR4: 100% accuracy ✓

---

## How to Track Progress

Each time you complete a phase:

```bash
cd "/home/z/Downloads/PAI/Assesment ind/Task 2"

# Run all tests
python -m unittest discover tests/ -v

# Check git log
git log --oneline | head -10

# See how many tests pass
python -m unittest discover tests/ -v 2>&1 | grep "Ran"
```

---

## Expected Final Statistics

| Metric | Target |
|--------|--------|
| Total Commits | ~25 |
| Total Tests | 32+ |
| Tests Passing | 32+ |
| Code Files (src/) | 4 |
| Test Files (tests/) | 7 |
| Lines of Code | ~400–500 |
| Test Coverage | >90% |
| Git History | Clean, atomic commits |

---

## When You're Done (Before Submission)

1. ✅ All 32+ tests passing
2. ✅ All phases complete (0–9)
3. ✅ Benchmark results captured
4. ✅ Report outline prepared (not in git)
5. ✅ Git log is clean (0–9 commits visible)
6. ✅ README and documentation complete
7. ✅ Code follows SOLID principles
8. ✅ Professional commit messages throughout

**Then:** Write your 750–1000 word reflective report using the outline provided.

---

**Current Status:** Phase 0 ✅ Complete | Ready for Phase 1 🚀
