#!/usr/bin/env python3
"""
Graph Visualization Script
Visualize the co-occurrence graph as text-based ASCII art and statistical summaries.
Shows network structure without external dependencies (networkx, matplotlib, etc).
"""

import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from transaction_loader import TransactionLoader
from cooccurrence_graph import CooccurrenceGraph
from query_service import QueryService


def print_header(title: str, width: int = 80):
    """Print formatted header."""
    print("\n" + "=" * width)
    print(f"  {title}".ljust(width - 1) + "=")
    print("=" * width + "\n")


def visualize_network_stats(service: QueryService, graph: CooccurrenceGraph):
    """Print network statistics."""
    print_header("NETWORK STATISTICS", 80)
    
    # Count vertices and edges
    num_vertices = len(graph.graph)
    unique_edges = graph.unique_edges()
    num_edges = len(unique_edges)
    
    print(f"📊 GRAPH METRICS:")
    print(f"   Vertices (Items):    {num_vertices:,}")
    print(f"   Edges (Pairs):       {num_edges:,}")
    print(f"   Density:             {(2 * num_edges) / (num_vertices * (num_vertices - 1)):.4f}")
    print(f"   Avg degree:          {(2 * num_edges) / num_vertices:.2f}\n")


def visualize_degree_distribution(graph: CooccurrenceGraph):
    """Show degree (connectivity) distribution."""
    print_header("DEGREE DISTRIBUTION (Top 20 Most Connected Items)", 80)
    
    degrees = []
    for item, neighbors in graph.graph.items():
        degree = len(neighbors)
        total_weight = sum(neighbors.values())
        degrees.append((item, degree, total_weight))
    
    # Sort by total weight (sum of all co-purchases)
    degrees.sort(key=lambda x: x[2], reverse=True)
    
    print(f"{'Rank':<5} {'Item':<25} {'Neighbors':<12} {'Total Weight':<15}")
    print("-" * 60)
    
    for rank, (item, degree, total_weight) in enumerate(degrees[:20], 1):
        print(f"{rank:<5} {item:<25} {degree:<12} {total_weight:<15,}")
    
    print(f"\n💡 Interpretation: 'Neighbors' = how many different items were bought with this item")
    print(f"                   'Total Weight' = total co-purchases with ALL neighbors\n")


def visualize_top_edges(service: QueryService):
    """Show top 20 most frequently co-purchased pairs."""
    print_header("TOP 20 STRONGEST CONNECTIONS (Most Co-Purchased Pairs)", 80)
    
    # Get top 20 bundles
    top_bundles = service.top_bundles(k=20)
    
    print(f"{'Rank':<5} {'Item 1':<20} {'Item 2':<20} {'Co-Purchases':<15} {'%':<8}")
    print("-" * 70)
    
    total_transactions = 14963  # From dataset
    
    for rank, (item1, item2, count) in enumerate(top_bundles, 1):
        percentage = (count / total_transactions) * 100
        print(f"{rank:<5} {item1:<20} {item2:<20} {count:<15} {percentage:>6.2f}%")
    
    print(f"\n💡 This represents the strongest relationships in the market basket.\n")


def visualize_item_neighbors(service: QueryService, item: str):
    """Show all neighbors of a specific item."""
    print_header(f"NEIGHBORS OF '{item.upper()}' (Top 15)", 80)
    
    results = service.top_with_item(item=item, k=15)
    
    if not results:
        print(f"❌ Item '{item}' not found in dataset.\n")
        return
    
    print(f"{'Rank':<5} {'Item':<25} {'Co-Purchases':<15} {'Strength':<15}")
    print("-" * 65)
    
    for rank, (neighbor, count) in enumerate(results, 1):
        # Calculate strength as percentage of main item purchases
        strength = "█" * min(20, count // 5)
        print(f"{rank:<5} {neighbor:<25} {count:<15} {strength}")
    
    print(f"\n💡 Shows which items are most frequently purchased with {item}.\n")


def visualize_bfs_network(service: QueryService, start_item: str, max_depth: int = 2):
    """Visualize BFS exploration as tree structure."""
    print_header(f"NETWORK EXPLORATION FROM '{start_item.upper()}' (BFS, depth={max_depth})", 80)
    
    results = service.bfs_related(start_item=start_item, max_depth=max_depth, min_weight=1)
    
    if not results or start_item not in results:
        print(f"❌ Item '{start_item}' not found.\n")
        return
    
    # Extract depth information
    depth_data = results[start_item]
    
    if not depth_data:
        print(f"❌ No neighbors found for '{start_item}'.\n")
        return
    
    # Print tree structure
    print(f"🔵 Depth 0 (Start):")
    print(f"   └─ {start_item}")
    
    for depth in sorted(depth_data.keys()):
        items = sorted(depth_data[depth])
        indent = "   " * (depth - 1)
        print(f"\n🔵 Depth {depth} ({len(items)} items):")
        for i, item in enumerate(items, 1):
            connector = "└─" if i == len(items) else "├─"
            print(f"{indent}   {connector} {item}")
    
    print(f"\n💡 Breadth-first traversal shows 1-hop and 2-hop relationships.\n")


def visualize_weight_distribution(graph: CooccurrenceGraph):
    """Show distribution of edge weights (co-purchase frequencies)."""
    print_header("EDGE WEIGHT DISTRIBUTION (Co-Purchase Frequency)", 80)
    
    edges = graph.unique_edges()
    weights = [w for _, _, w in edges]
    
    if not weights:
        print("No edges found.\n")
        return
    
    # Histogram buckets
    buckets = {
        "1-5": 0, "6-10": 0, "11-20": 0, "21-50": 0,
        "51-100": 0, "101-150": 0, "151-250": 0, "250+": 0
    }
    
    for w in weights:
        if w <= 5:
            buckets["1-5"] += 1
        elif w <= 10:
            buckets["6-10"] += 1
        elif w <= 20:
            buckets["11-20"] += 1
        elif w <= 50:
            buckets["21-50"] += 1
        elif w <= 100:
            buckets["51-100"] += 1
        elif w <= 150:
            buckets["101-150"] += 1
        elif w <= 250:
            buckets["151-250"] += 1
        else:
            buckets["250+"] += 1
    
    print(f"{'Weight Range':<15} {'Count':<10} {'Percentage':<12} {'Visualization':<40}")
    print("-" * 80)
    
    total = len(weights)
    for bucket, count in buckets.items():
        pct = (count / total) * 100 if total > 0 else 0
        bar_length = int(pct / 2)
        bar = "█" * bar_length
        print(f"{bucket:<15} {count:<10} {pct:>9.1f}% {bar}")
    
    print(f"\nTotal edges: {total:,}")
    print(f"Min weight:  {min(weights)}")
    print(f"Max weight:  {max(weights)}")
    print(f"Avg weight:  {sum(weights) / len(weights):.2f}\n")


def visualize_connected_components(graph: CooccurrenceGraph):
    """Show connected components (clusters of related items)."""
    print_header("CONNECTED COMPONENTS (Item Clusters)", 80)
    
    # Simple DFS to find components
    visited = set()
    components = []
    
    def dfs(item: str, component: set):
        """Depth-first search to find all connected items."""
        visited.add(item)
        component.add(item)
        for neighbor in graph.neighbors(item).keys():
            if neighbor not in visited:
                dfs(neighbor, component)
    
    for item in graph.graph.keys():
        if item not in visited:
            component = set()
            dfs(item, component)
            components.append(component)
    
    # Sort by size
    components.sort(key=len, reverse=True)
    
    print(f"{'Rank':<5} {'Size':<10} {'% of Graph':<15} {'Sample Items':<50}")
    print("-" * 80)
    
    total_items = len(graph.graph)
    for rank, component in enumerate(components[:10], 1):
        size = len(component)
        pct = (size / total_items) * 100
        samples = ", ".join(sorted(list(component))[:3])
        print(f"{rank:<5} {size:<10} {pct:>13.1f}% {samples}...")
    
    print(f"\nTotal components: {len(components)}")
    if len(components) == 1:
        print("🎯 Graph is fully connected (all items reachable from any item).\n")
    else:
        print(f"🎯 Graph has {len(components)} separate clusters.\n")


def visualize_item_summary(graph: CooccurrenceGraph):
    """Show overall item summary."""
    print_header("ITEM SUMMARY", 80)
    
    items = sorted(graph.graph.keys())
    
    print(f"Total items in dataset: {len(items)}\n")
    print("First 10 items (alphabetically):")
    for i, item in enumerate(items[:10], 1):
        neighbors = len(graph.neighbors(item))
        print(f"  {i:2d}. {item:<30} ({neighbors} co-purchasers)")
    
    print(f"\nLast 10 items (alphabetically):")
    for i, item in enumerate(items[-10:], 1):
        neighbors = len(graph.neighbors(item))
        print(f"  {i:2d}. {item:<30} ({neighbors} co-purchasers)")
    
    print()


def create_text_graph_art(service: QueryService):
    """Create ASCII art representation of top bundle network."""
    print_header("ASCII ART: TOP BUNDLE NETWORK", 80)
    
    top_bundles = service.top_bundles(k=15)
    
    print("Visual representation of top 15 strongest connections:\n")
    
    # Find all unique items in top bundles
    items_set = set()
    for item1, item2, weight in top_bundles:
        items_set.add(item1)
        items_set.add(item2)
    
    items = sorted(items_set)
    item_to_idx = {item: idx for idx, item in enumerate(items)}
    
    # Create adjacency for visualization
    connections = []
    for item1, item2, weight in top_bundles:
        idx1 = item_to_idx[item1]
        idx2 = item_to_idx[item2]
        connections.append((idx1, idx2, weight))
    
    # Print node list
    print("Nodes:")
    for idx, item in enumerate(items, 1):
        print(f"  {idx:2d}. {item}")
    
    print(f"\nConnections (co-purchases):")
    for idx1, idx2, weight in sorted(connections, key=lambda x: -x[2]):
        node1_name = items[idx1]
        node2_name = items[idx2]
        bar = "─" * (weight // 10)
        print(f"  {idx1+1:2d} ═{bar}═ {idx2+1:2d}  ({weight} times)")
    
    print("\n💡 Line thickness represents co-purchase strength.\n")


def main():
    """Run complete graph visualization."""
    # Load data
    print("\n📂 Loading data...")
    transactions = TransactionLoader.load_from_csv("data/Supermarket_dataset_PAI.csv")
    print(f"   ✅ Loaded {len(transactions):,} transactions\n")
    
    # Build graph
    print("🔗 Building co-occurrence graph...")
    graph = CooccurrenceGraph()
    for basket in transactions:
        graph.update_from_basket(basket)
    print(f"   ✅ Graph constructed\n")
    
    # Create service
    service = QueryService(graph)
    
    # Run visualizations
    print("\n" + "="*80)
    print(" "*20 + "MARKET BASKET ANALYSIS - GRAPH VISUALIZATION")
    print("="*80)
    
    visualize_network_stats(service, graph)
    visualize_degree_distribution(graph)
    visualize_top_edges(service)
    visualize_weight_distribution(graph)
    visualize_connected_components(graph)
    visualize_item_summary(graph)
    create_text_graph_art(service)
    
    # Interactive visualization of specific items
    print_header("INTERACTIVE ITEM EXPLORATION", 80)
    print("Example: Items bought with 'Whole Milk':\n")
    visualize_item_neighbors(service, "whole milk")
    
    print("Example: Items 2 hops away from 'Whole Milk':\n")
    visualize_bfs_network(service, "whole milk", max_depth=2)
    
    print_header("VISUALIZATION COMPLETE", 80)
    print("✨ All graph visualizations have been generated above.\n")


if __name__ == "__main__":
    main()
