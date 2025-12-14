Below is the **full context + task interpretation + complete plan** (requirements → design → algorithms → TDD workflow → deliverables) written so you can see the entire scope end-to-end and know exactly what you are doing and why. I will also explicitly include the **TDD + Git cadence** you asked for: “write tests → commit failing tests → implement → commit passing code”.

---

# 1) Full context: what Task 2 is and what you are being graded on

## 1.1 Scenario context (supermarket)

You have thousands of supermarket transactions (“market baskets”).
Each transaction is the set/list of items bought in one shopping visit.

The supermarket wants you to efficiently answer:

* **Q1:** “Which items are most frequently bought together with bread?”
* **Q2:** “What are the top three most common product bundles across all transactions?”
* **Q3:** “How can we quickly identify whether two items are often co-purchased?”

## 1.2 What Task 2 is actually assessing

Your grade is not for “finding clever patterns with ML.” Your grade is for demonstrating:

1. **Correct data structure choice** (graph/tree/queue-based etc.)
2. **Algorithms from your module operating on that structure** (sorting/ranking, searching/lookup, BFS/DFS traversal)
3. **An application extension** (visualisation/presentation + filters + recommendation-style query)
4. **Professional software engineering**:

   * requirements (FR/NFR)
   * OOP structure (SRP, encapsulation)
   * TDD with automated tests 
   * version control discipline 
5. **Reflective report (750–1000 words)**:

   * justify design
   * complexity analysis
   * discuss alternatives
   * evaluate scalability

---

# 2) The task requirements (what we must implement)

## 2.1 User requirements (high-level)

* Analysts can identify co-purchased products.
* Analysts can quickly check association strength between any two items.
* Analysts can run common queries easily.

## 2.2 System requirements (detailed)

### Functional Requirements (FRs)

We will implement **and test**:

* **FR1** Ingest transaction data and represent each transaction as a basket (list of item names).
* **FR2** Build co-occurrence counts for item pairs in the same basket.
* **FR3** Retrieve co-purchase frequency for a given item pair.
* **FR4** Return the **top K** most common bundles across all transactions (bundle = item pair).
* **FR5** For a given item X (e.g., bread), return top items bought with X (ranked).
* **FR6** Provide a “visualisation/presentation” that highlights the strongest associations.
* **FR7** Provide filters for exploration (e.g., minimum frequency threshold, depth limit) and optionally BFS/DFS.
* **FR8** Support updating the structure when new transactions arrive (incremental update, no full rebuild).

### Quantitative Non-Functional Requirements (NFRs)

These must be measurable (your module emphasizes quantitative NFRs). 

* **NFR1 (Lookup):** pair-frequency lookup must complete in **< 50 ms**.
* **NFR2 (Build rate):** initial build must process **≥ 1000 transactions/sec**.
* **NFR3 (Responsiveness):** top-K output must display in **< 1 sec**.
* **NFR4 (Correctness):** 100% accuracy of co-occurrence counts (no missing/double counting).

---

# 3) The core idea (how the system works)

## 3.1 Turn baskets into a “relationship network”

Items that appear together become linked. We count how often.

Example baskets:

* `[bread, milk, eggs]`
* `[bread, milk]`
* `[milk, cereal]`

Then:

* bread—milk weight 2
* bread—eggs weight 1
* milk—eggs weight 1
* milk—cereal weight 1

## 3.2 Data structure: weighted undirected graph (adjacency list)

We store it as nested dictionaries (in-scope DS; dictionaries are hash maps with average O(1) lookup). 

Conceptual structure:

```text
graph["bread"]["milk"] = 2
graph["milk"]["bread"] = 2
```

Why this is perfect for the queries:

* Q3 (pair check) is one dict lookup → fast
* Q1 (items bought with bread) = look at neighbors of bread and sort
* Q2 (top bundles) = list all edges and sort

---

# 4) Algorithms we will use (module-aligned)

## 4.1 Graph construction (FR2, FR8)

For each basket of size m:

* generate all unordered pairs (i, j) with i < j
* increment weight for each pair

Complexity:

* Pair generation per basket: **O(m²)** (nested loops)
* Increment: **O(1)** average per pair (dict lookup) 
* Total build: Σ O(m²) over all transactions (discuss this in report)

## 4.2 FR3 Pair frequency lookup

* `weight = graph[a].get(b, 0)`
  Average complexity: **O(1)** 

## 4.3 FR5 “Bought with bread” recommendation

* neighbors = graph["bread"]
* sort by weight descending
  Complexity: **O(deg(bread) log deg(bread))**

## 4.4 FR4 Top-K bundles globally

* extract unique edges once (only keep (a,b) where a < b)
* sort by weight descending
  Complexity: **O(E log E)** where E is number of unique pairs

## 4.5 FR7 BFS/DFS exploration (optional but recommended)

* BFS using a queue (FIFO) to explore relationship layers
* DFS using a stack (LIFO) to explore depth-first
* add filters: min weight threshold, max depth
  Complexity: **O(V + E)** on visited subgraph

---

# 5) Software architecture (OOP, testable)

We keep it simple and modular (fits testing guidance: separate files, test each unit). 

### Modules / classes

1. **TransactionLoader**

* reads raw data format
* outputs baskets: `List[List[str]]`
* handles cleaning: trim whitespace, ignore empty items, deduplicate within basket

2. **CooccurrenceGraph (Repository)**

* owns adjacency dict
* methods:

  * `update_from_basket(basket)`
  * `get_weight(a,b)`
  * `neighbors(item)`
  * `unique_edges()`

3. **QueryService**

* implements FR3/FR4/FR5/FR7 using the graph
* returns results in structured form (lists of tuples)

4. **Presenter (FR6)**

* text-based “visualisation” by default:

  * top edges list
  * bread neighbor list
  * filtered views
    (Optional matplotlib later, but not required.)

---

# 6) Fine-grained TDD plan with your requested “commit cadence”

You asked for:
**write failing tests → commit failing tests → implement → commit passing code**.

That is exactly the workflow we will use, and it also produces excellent evidence of TDD and version control practice.  

## Global rule for each feature (each FR)

For every requirement chunk:

1. **Write tests first** (they fail because feature doesn’t exist yet)
2. **Commit the failing tests**
   Commit message example:
   `test(FR2): add failing tests for basket pair updates`
3. Implement minimal production code until tests pass
4. **Commit passing code**
   Commit message example:
   `feat(FR2): implement graph update from basket`
5. Refactor if needed (tests still pass)
6. Optional: commit refactor separately

This is clean, professional, and matches the module’s focus on automated testing and version control discipline.  

---

## Phase-by-phase TDD breakdown (very detailed)

### Phase 0 — Scaffold repository

**Goal:** project runs tests at all.

* Create folders: `src/`, `tests/`
* Add `README.md`, `.gitignore`
* Add `tests/test_smoke.py`

**Commit:**

* `chore: scaffold project structure and smoke test`

---

### Phase 1 — FR1 Transaction ingestion → baskets

**Goal:** Convert input rows into baskets.

#### Tests (write first, then commit failing)

* FR1-T1: grouping by transaction id produces correct baskets
* FR1-T2: deduplicate item repeated in same basket
* FR1-T3: ignore empty/null item names
* FR1-T4: deterministic ordering inside baskets (sorted)

**Commit failing tests:**
`test(FR1): add failing tests for basket building`

#### Implementation (make tests pass)

* Implement `TransactionLoader.to_baskets(...)`

**Commit passing code:**
`feat(FR1): implement transaction loader to build baskets`

---

### Phase 2 — FR2/FR8 Graph build + incremental updates

**Goal:** Update edge weights correctly from baskets.

#### Tests (write first, then commit failing)

* FR2-T1: new graph returns 0 for unseen pair
* FR2-T2: basket [A,B] increments both directions (symmetry)
* FR2-T3: basket [A,B,C] increments all 3 pairs
* FR8-T1: second basket updates counts incrementally
* FR2-T4: no self edges

**Commit failing tests:**
`test(FR2,FR8): add failing tests for graph updates`

#### Implementation (make tests pass)

* Implement `CooccurrenceGraph.update_from_basket`
* Implement `get_weight`, `neighbors`

**Commit passing code:**
`feat(FR2,FR8): implement cooccurrence graph with incremental updates`

---

### Phase 3 — FR3 Pair frequency query

**Goal:** Fast lookup + “often co-purchased” boolean.

#### Tests

* FR3-T1: missing pair returns 0
* FR3-T2: known pair returns correct count
* FR3-T3: threshold logic (>= threshold)

**Commit failing tests:**
`test(FR3): add failing tests for pair frequency and threshold check`

#### Implementation

* `QueryService.pair_frequency`
* `QueryService.often_copurchased`

**Commit passing code:**
`feat(FR3): implement pair frequency lookup and co-purchase check`

---

### Phase 4 — FR5 “Bought with bread” recommendation

**Goal:** Rank neighbors of an item by weight.

#### Tests

* FR5-T1: results sorted by weight desc
* FR5-T2: limit to k
* FR5-T3: missing item returns []
* FR5-T4: deterministic tie-break rule

**Commit failing tests:**
`test(FR5): add failing tests for top-with-item ranking`

#### Implementation

* `QueryService.top_with_item(item, k)`

**Commit passing code:**
`feat(FR5): implement top-with-item recommendation query`

---

### Phase 5 — FR4 Top-K bundles (pairs)

**Goal:** Return global top pairs.

#### Tests

* FR4-T1: unique edges only (avoid double counting A-B and B-A)
* FR4-T2: correct ordering
* FR4-T3: k larger than edges returns all
* FR4-T4: tie-break deterministic

**Commit failing tests:**
`test(FR4): add failing tests for top-k bundles`

#### Implementation

* `CooccurrenceGraph.unique_edges()`
* `QueryService.top_bundles(k)`

**Commit passing code:**
`feat(FR4): implement top-k bundles ranking`

---

### Phase 6 — FR7 Filters + BFS/DFS exploration

**Goal:** Explore relationships beyond direct neighbors.

#### Tests

* FR7-T1: BFS depth=1 returns direct neighbors
* FR7-T2: BFS depth=2 returns second-hop nodes
* FR7-T3: min_weight filter blocks weak edges
* FR7-T4: cycles don’t loop forever (visited set)

**Commit failing tests:**
`test(FR7): add failing tests for BFS exploration with filters`

#### Implementation

* `QueryService.bfs_related(start, max_depth, min_weight)`

**Commit passing code:**
`feat(FR7): implement BFS relationship exploration with filters`

---

### Phase 7 — FR6 Visualisation / presentation

**Goal:** Highlight strongest associations.

Because matplotlib is not mandated, we implement **text visualisation** that is clearly justified.

#### Tests

* FR6-T1: presenter returns top N edges
* FR6-T2: respects min_weight threshold
* FR6-T3: handles empty graph cleanly

**Commit failing tests:**
`test(FR6): add failing tests for relationship presentation`

#### Implementation

* `Presenter.top_edges(top_n, min_weight)`
* `Presenter.format_*()` for clean output

**Commit passing code:**
`feat(FR6): implement text-based visualisation of strongest associations`

(Optional later: add matplotlib and test only edge-selection logic, not pixels.)

---

### Phase 8 — Benchmarks to support NFRs (for report evidence)

**Goal:** Measure, don’t just claim.

Create `benchmarks/run.py` (not unit tests) to time:

* build transactions/sec (NFR2)
* repeated pair lookup average time (NFR1)
* top-K queries runtime (NFR3)

**Commit:**
`chore: add benchmark script for NFR measurements`

---

# 7) What you will submit (deliverables checklist)

## Code deliverables

* `src/` modules (loader, graph, queries, presenter)
* `tests/` unit tests (unittest)
* Dataset loader path or instructions
* Optional benchmark script

## Report deliverable (750–1000 words)

You will write:

1. Justification: why graph + dict adjacency list + sorting + BFS
2. Complexity: build O(Σm²), lookup O(1), ranking O(E log E), BFS O(V+E)
3. Alternatives: list-of-pairs, matrix, Apriori (explain why out of scope)
4. Scalability: larger data, dynamic updates (FR8), memory growth
5. Evidence: benchmark numbers for NFRs

---

# 8) One scope lock (so everything stays consistent)

We will define **“bundle” = pair of items**.
That matches the graph edge concept and keeps the solution simple and in-scope.


