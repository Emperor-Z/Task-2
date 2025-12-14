#!/usr/bin/env python3
"""
Interactive CLI for Market Basket Analysis System
Allows users to query co-purchase relationships in supermarket data.
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from transaction_loader import TransactionLoader
from cooccurrence_graph import CooccurrenceGraph
from query_service import QueryService
from presenter import Presenter


# Configure logging
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f"cli_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def print_header():
    """Print application header."""
    print("\n" + "=" * 70)
    print("MARKET BASKET ANALYSIS - INTERACTIVE CLI")
    print("=" * 70)
    print("Supermarket co-purchase explorer")
    print(f"Session log: {LOG_FILE}\n")
    logger.info("=== CLI SESSION STARTED ===")


def print_menu():
    """Print main menu options."""
    print("\n--- MAIN MENU ---")
    print("1. Find items bought with [ITEM]")
    print("2. Find top bundles (most frequently co-purchased pairs)")
    print("3. Check co-purchase frequency between two items")
    print("4. Explore related items (BFS)")
    print("5. List available items")
    print("6. Load new dataset (reload CSV)")
    print("0. Exit\n")


def find_item_fuzzy(graph, search_term):
    """Find item in graph (case-insensitive, fuzzy match).
    
    Returns:
        - Single item string if exact match found
        - List of items if partial matches found
        - None if no matches found
    """
    search_lower = search_term.lower().strip()
    all_items = sorted(list(graph.graph.keys()))
    
    # Exact match (case-insensitive)
    for item in all_items:
        if item.lower() == search_lower:
            return item
    
    # Partial match - sorted for consistency
    matches = [item for item in all_items if search_lower in item.lower()]
    return matches if matches else None


def prompt_choose_item(matches, search_term):
    """Prompt user to choose from multiple matching items.
    
    Args:
        matches: List of matching item names
        search_term: Original search term
        
    Returns:
        Selected item name or None if user cancels
    """
    print(f"\n📋 Found {len(matches)} items matching '{search_term}':\n")
    
    for i, item in enumerate(matches, 1):
        print(f"  {i}. {item}")
    
    print(f"  0. Cancel\n")
    
    while True:
        try:
            choice = input("Select item number: ").strip()
            choice_num = int(choice)
            
            if choice_num == 0:
                print("❌ Cancelled")
                return None
            elif 1 <= choice_num <= len(matches):
                selected = matches[choice_num - 1]
                logger.info(f"User selected: {selected} (from {len(matches)} matches for '{search_term}')")
                return selected
            else:
                print(f"❌ Please enter 0-{len(matches)}")
        except ValueError:
            print("❌ Please enter a valid number")


def list_available_items(graph):
    """List all available items in the dataset."""
    all_items = sorted(list(graph.graph.keys()))
    print(f"\n📋 Available items ({len(all_items)} total):\n")
    
    # Print in columns
    for i, item in enumerate(all_items, 1):
        print(f"  {i:3d}. {item}")
        if i % 2 == 0:
            print()
    
    logger.info(f"Listed {len(all_items)} available items")


def query_top_items(query_service, graph, presenter):
    """Query top items bought with a specific item."""
    item_search = input("Enter item name: ").strip()
    if not item_search:
        print("❌ Item name cannot be empty")
        return

    # Find item (case-insensitive)
    result = find_item_fuzzy(graph, item_search)
    
    if isinstance(result, list):
        # Multiple matches - let user choose
        item = prompt_choose_item(result, item_search)
        if item is None:
            return
    elif result is None:
        print(f"❌ '{item_search}' not found in dataset")
        logger.warning(f"Item not found: {item_search}")
        return
    else:
        # Single exact match
        item = result

    try:
        k = int(input("How many top items? (default 10): ") or "10")
        if k < 1:
            print("❌ K must be at least 1")
            return
    except ValueError:
        print("❌ Invalid number")
        return

    results = query_service.top_with_item(item, k)
    if not results:
        print(f"❌ No items found co-purchased with '{item}'")
        logger.info(f"Query: top_with_item('{item}', {k}) - No results")
        return

    output = presenter.format_recommendations(results, item)
    print("\n" + output)
    logger.info(f"Query: top_with_item('{item}', {k}) - {len(results)} results")


def query_top_bundles(query_service, presenter):
    """Query top bundles."""
    try:
        k = int(input("How many top bundles? (default 10): ") or "10")
        if k < 1:
            print("❌ K must be at least 1")
            return
    except ValueError:
        print("❌ Invalid number")
        return

    results = query_service.top_bundles(k)
    if not results:
        print("❌ No bundles found in dataset")
        logger.warning("Query: top_bundles - No results")
        return

    output = presenter.format_top_bundles(results)
    print("\n" + output)
    logger.info(f"Query: top_bundles({k}) - {len(results)} results")


def query_pair_frequency(query_service, graph):
    """Query frequency of item pair."""
    item1_search = input("Enter first item: ").strip()
    item2_search = input("Enter second item: ").strip()

    if not item1_search or not item2_search:
        print("❌ Both item names are required")
        return

    # Find first item
    result1 = find_item_fuzzy(graph, item1_search)
    if isinstance(result1, list):
        item1 = prompt_choose_item(result1, item1_search)
        if item1 is None:
            return
    elif result1 is None:
        print(f"❌ '{item1_search}' not found")
        logger.warning(f"Item not found: {item1_search}")
        return
    else:
        item1 = result1

    # Find second item
    result2 = find_item_fuzzy(graph, item2_search)
    if isinstance(result2, list):
        item2 = prompt_choose_item(result2, item2_search)
        if item2 is None:
            return
    elif result2 is None:
        print(f"❌ '{item2_search}' not found")
        logger.warning(f"Item not found: {item2_search}")
        return
    else:
        item2 = result2

    freq = query_service.pair_frequency(item1, item2)
    if freq == 0:
        print(f"❌ '{item1}' and '{item2}' were never purchased together")
        logger.info(f"Query: pair_frequency('{item1}', '{item2}') - 0")
    else:
        print(f"✅ '{item1}' and '{item2}' were purchased together {freq} times")
        logger.info(f"Query: pair_frequency('{item1}', '{item2}') - {freq}")


def explore_related(query_service, graph, presenter):
    """Explore related items via BFS."""
    item_search = input("Enter item name: ").strip()
    if not item_search:
        print("❌ Item name cannot be empty")
        return

    # Find item (case-insensitive)
    result = find_item_fuzzy(graph, item_search)
    
    if isinstance(result, list):
        # Multiple matches - let user choose
        item = prompt_choose_item(result, item_search)
        if item is None:
            return
    elif result is None:
        print(f"❌ '{item_search}' not found in dataset")
        logger.warning(f"Item not found: {item_search} (BFS)")
        return
    else:
        # Single exact match
        item = result

    try:
        max_depth = int(input("Max exploration depth? (default 2): ") or "2")
        min_weight = int(input("Minimum co-purchase frequency? (default 1): ") or "1")
        
        if max_depth < 1 or min_weight < 1:
            print("❌ Values must be at least 1")
            return
    except ValueError:
        print("❌ Invalid numbers")
        return

    results = query_service.bfs_related(item, max_depth, min_weight)
    if not results or not any(results[item].values()):
        print(f"❌ No related items found for '{item}' within {max_depth} degrees")
        logger.info(f"Query: bfs_related('{item}', {max_depth}, {min_weight}) - No results")
        return

    print(f"\n📊 Items related to '{item}' (within {max_depth} degrees, min frequency {min_weight}):\n")
    
    # Print results by depth
    total_items = 0
    for depth in sorted(results[item].keys()):
        items_at_depth = results[item][depth]
        if items_at_depth:
            total_items += len(items_at_depth)
            print(f"  Degree {depth}: {', '.join(sorted(items_at_depth))}")
    print()
    logger.info(f"Query: bfs_related('{item}', {max_depth}, {min_weight}) - {total_items} items")


def load_dataset(csv_path):
    """Load dataset and build graph."""
    print(f"\n📂 Loading dataset from {csv_path}...")
    
    try:
        loader = TransactionLoader()
        baskets = loader.load_from_csv(csv_path)
        print(f"✅ Loaded {len(baskets)} transactions")
        logger.info(f"Loaded {len(baskets)} transactions from {csv_path}")

        print("🔗 Building co-occurrence graph...")
        graph = CooccurrenceGraph()
        for basket in baskets:
            graph.update_from_basket(basket)
        
        unique_edges = len(graph.unique_edges())
        all_items = len(graph.graph)
        print(f"✅ Built graph with {all_items} items and {unique_edges} unique item pairs")
        logger.info(f"Built graph: {all_items} items, {unique_edges} edges")

        query_service = QueryService(graph)
        return query_service, graph
    except FileNotFoundError:
        print(f"❌ File not found: {csv_path}")
        logger.error(f"File not found: {csv_path}")
        return None, None
    except KeyError as e:
        print(f"❌ CSV format error (missing column): {e}")
        logger.error(f"CSV format error: {e}")
        return None, None
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        logger.error(f"Error loading dataset: {e}")
        return None, None


def main():
    """Main CLI loop."""
    print_header()

    # Find CSV file
    csv_path = Path(__file__).parent / "data" / "Supermarket_dataset_PAI.csv"
    
    if not csv_path.exists():
        print(f"❌ Dataset not found at {csv_path}")
        print("Please ensure data/Supermarket_dataset_PAI.csv exists")
        logger.error(f"Dataset not found: {csv_path}")
        sys.exit(1)

    # Load initial dataset
    query_service, graph = load_dataset(csv_path)
    if query_service is None:
        sys.exit(1)

    presenter = Presenter()

    # Main loop
    while True:
        print_menu()
        choice = input("Select option: ").strip()

        if choice == "0":
            print("\n✅ Goodbye!\n")
            logger.info("=== CLI SESSION ENDED ===")
            break
        elif choice == "1":
            query_top_items(query_service, graph, presenter)
        elif choice == "2":
            query_top_bundles(query_service, presenter)
        elif choice == "3":
            query_pair_frequency(query_service, graph)
        elif choice == "4":
            explore_related(query_service, graph, presenter)
        elif choice == "5":
            list_available_items(graph)
        elif choice == "6":
            query_service, graph = load_dataset(csv_path)
            if query_service is None:
                print("❌ Failed to reload dataset")
                logger.error("Failed to reload dataset")
        else:
            print("❌ Invalid option. Please select 0-6")
            logger.warning(f"Invalid menu option: {choice}")


if __name__ == "__main__":
    main()
