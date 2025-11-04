import networkx as nx
import pandas as pd
import os

CSV_PATH = r"d:\Rtamanyu\_IIt Madras\2nd year\sem 1\Tools in datascience\Week 7\q-network-python-centrality.csv"


def load_graph_from_csv(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV not found at {path}")
    # Use a file handle to skip header then pass to nx.read_edgelist
    with open(path, 'r', encoding='utf-8') as f:
        header = next(f)
        G = nx.read_edgelist(f, delimiter=',', create_using=nx.Graph())
    return G


if __name__ == '__main__':
    G = load_graph_from_csv(CSV_PATH)
    print(f"Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # Compute betweenness centrality
    centrality = nx.betweenness_centrality(G)

    # Sort descending
    top_sorted = sorted(centrality.items(), key=lambda x: x[1], reverse=True)

    # Print top 3 for sanity
    print("\nTop 3 nodes by betweenness centrality:")
    for node, score in top_sorted[:3]:
        print(f"{node}: {score:.6f}")

    top_node, top_score = top_sorted[0]
    print(f"\nNode with highest betweenness centrality: {top_node} (score {top_score:.6f})")
