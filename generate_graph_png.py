#!/usr/bin/env python3
"""
Generate PNG graph diagram using matplotlib
Shows co-occurrence network visualization with top bundles and connections.
"""

import sys
from pathlib import Path
from collections import defaultdict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from transaction_loader import TransactionLoader
from cooccurrence_graph import CooccurrenceGraph
from query_service import QueryService

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import networkx as nx
import numpy as np


def create_top_bundles_graph(service: QueryService, graph: CooccurrenceGraph):
    """Create a focused graph of top 20 bundles."""
    print("📊 Creating top bundles visualization...")
    
    # Get top 20 bundles
    top_bundles = service.top_bundles(k=20)
    
    # Create networkx graph
    G = nx.Graph()
    
    # Add edges with weights
    for item1, item2, weight in top_bundles:
        G.add_edge(item1, item2, weight=weight)
    
    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    
    # Use spring layout with tuned parameters
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42, scale=2)
    
    # Draw edges with width proportional to weight
    edges = G.edges()
    weights = [G[u][v]['weight'] for u, v in edges]
    max_weight = max(weights)
    
    # Normalize weights to line widths (0.5 to 8)
    line_widths = [0.5 + (w / max_weight) * 7.5 for w in weights]
    
    # Draw edges
    for (u, v), width in zip(edges, line_widths):
        ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], 
                'gray', alpha=0.3, linewidth=width, zorder=1)
    
    # Draw nodes
    node_colors = []
    node_sizes = []
    
    for node in G.nodes():
        # Size based on degree
        degree = G.degree(node)
        size = 800 + (degree * 50)
        node_sizes.append(size)
        
        # Color based on degree
        if degree >= 15:
            node_colors.append('#FF6B6B')  # Red - hub
        elif degree >= 10:
            node_colors.append('#FFA500')  # Orange - major
        else:
            node_colors.append('#4ECDC4')  # Teal - minor
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                          node_size=node_sizes, ax=ax, alpha=0.9)
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold', ax=ax)
    
    # Add title and legend
    ax.set_title('Market Basket Analysis - Top 20 Co-Purchase Bundles\n' + 
                 'Node size = connectivity, Edge thickness = frequency',
                 fontsize=16, fontweight='bold', pad=20)
    
    # Legend
    legend_elements = [
        mpatches.Patch(color='#FF6B6B', label='Hub Items (degree ≥ 15)'),
        mpatches.Patch(color='#FFA500', label='Major Items (degree 10-14)'),
        mpatches.Patch(color='#4ECDC4', label='Minor Items (degree < 10)'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=11)
    
    ax.axis('off')
    plt.tight_layout()
    
    # Save
    output_file = "graph_top_bundles.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ Saved: {output_file}")
    plt.close()


def create_full_network_graph(graph: CooccurrenceGraph):
    """Create visualization of full network with all items."""
    print("📊 Creating full network visualization...")
    
    # Create networkx graph from cooccurrence data
    G = nx.Graph()
    
    # Add all edges with weights
    for item, neighbors in graph.graph.items():
        for neighbor, weight in neighbors.items():
            if item < neighbor:  # Avoid duplicates
                G.add_edge(item, neighbor, weight=weight)
    
    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(20, 16))
    
    # Use spring layout
    print("   Calculating layout (this may take a moment)...")
    pos = nx.spring_layout(G, k=0.5, iterations=20, seed=42, scale=3)
    
    # Filter edges by weight for clarity (only show weight >= 5)
    strong_edges = [(u, v, d['weight']) for u, v, d in G.edges(data=True) if d['weight'] >= 5]
    
    # Draw only strong edges
    for u, v, weight in strong_edges:
        width = min(5, weight / 50)  # Cap at 5 for visibility
        ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], 
                'lightgray', alpha=0.2, linewidth=width, zorder=1)
    
    # Draw all nodes
    node_colors = []
    node_sizes = []
    
    for node in G.nodes():
        degree = G.degree(node)
        size = 100 + (degree * 5)
        node_sizes.append(size)
        
        if degree >= 100:
            node_colors.append('#FF1744')  # Deep red
        elif degree >= 75:
            node_colors.append('#FF5722')  # Orange
        elif degree >= 50:
            node_colors.append('#FFC107')  # Amber
        elif degree >= 25:
            node_colors.append('#4CAF50')  # Green
        else:
            node_colors.append('#2196F3')  # Blue
    
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                          node_size=node_sizes, ax=ax, alpha=0.8)
    
    # Draw labels for high-degree nodes only
    high_degree_labels = {node: node for node in G.nodes() 
                         if G.degree(node) >= 50}
    nx.draw_networkx_labels(G, pos, labels=high_degree_labels, font_size=8, 
                           font_weight='bold', ax=ax)
    
    ax.set_title('Market Basket Analysis - Full Network\n' + 
                 '167 items, 6,260 pairs (showing edges with weight ≥ 5)',
                 fontsize=16, fontweight='bold', pad=20)
    
    # Legend
    legend_elements = [
        mpatches.Patch(color='#FF1744', label='Very High Connectivity (≥100 neighbors)'),
        mpatches.Patch(color='#FF5722', label='High Connectivity (75-99 neighbors)'),
        mpatches.Patch(color='#FFC107', label='Medium Connectivity (50-74 neighbors)'),
        mpatches.Patch(color='#4CAF50', label='Low Connectivity (25-49 neighbors)'),
        mpatches.Patch(color='#2196F3', label='Very Low Connectivity (<25 neighbors)'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=10)
    
    ax.axis('off')
    plt.tight_layout()
    
    # Save
    output_file = "graph_full_network.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ Saved: {output_file}")
    plt.close()


def create_hub_network_graph(service: QueryService, graph: CooccurrenceGraph):
    """Create focused graph of milk and its top neighbors."""
    print("📊 Creating hub network visualization (Whole Milk focus)...")
    
    # Get top neighbors of milk
    milk_neighbors = service.top_with_item("whole milk", k=30)
    
    # Create graph
    G = nx.Graph()
    G.add_node("whole milk")
    
    for item, weight in milk_neighbors:
        G.add_edge("whole milk", item, weight=weight)
    
    # Add connections between neighbors
    for i, (item1, weight1) in enumerate(milk_neighbors[:15]):
        for item2, weight2 in milk_neighbors[i+1:15]:
            w = graph.get_weight(item1, item2)
            if w > 0:
                G.add_edge(item1, item2, weight=w)
    
    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    
    # Use circular layout with milk in center
    pos = {}
    pos["whole milk"] = (0, 0)
    
    # Place neighbors in circle
    neighbor_count = len([n for n in G.nodes() if n != "whole milk"])
    for i, node in enumerate([n for n in G.nodes() if n != "whole milk"]):
        angle = 2 * 3.14159 * i / neighbor_count
        pos[node] = (3 * (i / neighbor_count) * 2 * 3.14159 / (2 * 3.14159) * 5 * (0.5 + 0.5 * (i % 2)), 
                     3 * (0.5 + 0.5 * (i % 2)) * (i / neighbor_count))
    
    # Actually use spring layout - it's better
    pos = nx.spring_layout(G, k=2, iterations=30, seed=42, scale=2)
    
    # Draw edges
    edges = G.edges(data=True)
    for u, v, d in edges:
        width = 1 if d['weight'] < 50 else min(8, d['weight'] / 30)
        alpha = 0.3 if d['weight'] < 50 else 0.6
        ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], 
                'gray', alpha=alpha, linewidth=width, zorder=1)
    
    # Draw nodes
    node_colors = []
    node_sizes = []
    
    for node in G.nodes():
        if node == "whole milk":
            node_colors.append('#FF1744')
            node_sizes.append(3000)
        else:
            # Size by connection to milk
            milk_weight = G[node]["whole milk"]["weight"] if "whole milk" in G[node] else 0
            size = 1000 + milk_weight * 5
            node_sizes.append(size)
            
            degree = G.degree(node)
            if degree >= 20:
                node_colors.append('#FFA500')
            else:
                node_colors.append('#4ECDC4')
    
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                          node_size=node_sizes, ax=ax, alpha=0.9)
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold', ax=ax)
    
    ax.set_title('Market Basket Analysis - Whole Milk Hub Network\n' + 
                 'Showing Milk, Top 30 Co-Purchasers, and Their Connections',
                 fontsize=16, fontweight='bold', pad=20)
    
    # Legend
    legend_elements = [
        mpatches.Patch(color='#FF1744', label='Whole Milk (Hub)'),
        mpatches.Patch(color='#FFA500', label='High-Degree Neighbors'),
        mpatches.Patch(color='#4ECDC4', label='Other Neighbors'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=11)
    
    ax.axis('off')
    plt.tight_layout()
    
    # Save
    output_file = "graph_milk_hub.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ Saved: {output_file}")
    plt.close()


def create_bundle_heatmap(service: QueryService):
    """Create heatmap of top 20 items co-purchases."""
    print("📊 Creating bundle heatmap...")
    
    # Get top 20 bundles
    top_bundles = service.top_bundles(k=20)
    
    # Extract unique items
    items = set()
    bundle_dict = defaultdict(lambda: defaultdict(int))
    
    for item1, item2, weight in top_bundles:
        items.add(item1)
        items.add(item2)
        bundle_dict[item1][item2] = weight
        bundle_dict[item2][item1] = weight
    
    items = sorted(items)
    n = len(items)
    
    # Create matrix
    matrix = []
    for i in items:
        row = []
        for j in items:
            if i in bundle_dict and j in bundle_dict[i]:
                row.append(bundle_dict[i][j])
            elif i == j:
                row.append(0)
            else:
                row.append(0)
        matrix.append(row)
    
    # Create heatmap
    data = np.array(matrix)
    
    fig, ax = plt.subplots(figsize=(14, 12))
    
    im = ax.imshow(data, cmap='YlOrRd', aspect='auto')
    
    # Set ticks and labels
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(items, rotation=45, ha='right', fontsize=9)
    ax.set_yticklabels(items, fontsize=9)
    
    # Add text annotations
    for i in range(n):
        for j in range(n):
            if data[i, j] > 0:
                text = ax.text(j, i, int(data[i, j]),
                             ha="center", va="center", color="black", fontsize=8)
    
    ax.set_title('Co-Purchase Frequency Heatmap - Top Items\n' +
                'Showing frequency of joint purchases (darker = more frequent)',
                fontsize=14, fontweight='bold', pad=20)
    
    plt.colorbar(im, ax=ax, label='Co-Purchase Frequency')
    plt.tight_layout()
    
    # Save
    output_file = "graph_bundle_heatmap.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ Saved: {output_file}")
    plt.close()


def main():
    """Generate all graph visualizations."""
    print("\n" + "="*80)
    print(" "*15 + "MARKET BASKET ANALYSIS - PNG GRAPH GENERATOR")
    print("="*80 + "\n")
    
    # Load data
    print("📂 Loading data...")
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
    
    # Generate visualizations
    print("🎨 Generating PNG diagrams...\n")
    
    create_top_bundles_graph(service, graph)
    create_hub_network_graph(service, graph)
    create_bundle_heatmap(service)
    create_full_network_graph(graph)
    
    print("\n" + "="*80)
    print("✨ All graph visualizations generated successfully!")
    print("="*80)
    print("\nGenerated files:")
    print("  1. graph_top_bundles.png - Top 20 co-purchased bundles")
    print("  2. graph_milk_hub.png - Whole milk and its network")
    print("  3. graph_bundle_heatmap.png - Frequency heatmap")
    print("  4. graph_full_network.png - Complete 167-item network")
    print("\n")


if __name__ == "__main__":
    main()
