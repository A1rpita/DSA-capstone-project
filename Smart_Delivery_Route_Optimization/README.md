# Smart Delivery Route Optimization System

## Overview
A Python/Streamlit mini-project that models delivery locations as a weighted graph,
uses Dijkstra's algorithm for shortest paths, applies a greedy nearest-neighbour
heuristic for delivery sequencing, and visualizes routes and performance metrics.

## Requirements
- Python 3.9+
- Streamlit
- NetworkX
- Matplotlib
- Pandas

## Setup
```bash
python -m venv .venv
```
Windows:
```bash
.venv\Scripts\activate
```
Install dependencies:
```bash
pip install -r requirements.txt
```
Run:
```bash
streamlit run app.py
```
Open the local URL shown in the terminal (normally http://localhost:8501).

## Algorithms
1. Weighted undirected graph: locations are nodes and roads are edges weighted by kilometres.
2. Dijkstra: calculates the shortest road path and distance between two nodes.
3. Greedy nearest neighbour: repeatedly selects the unvisited delivery location with
   the smallest shortest-path distance from the current location.
4. Metrics: optimized distance, estimated driving/service time, and comparison against
   a simple alphabetical reference order.

## Limitations
The data is simulated. The application does not use live maps, traffic, vehicle capacity,
time windows, or multiple vehicles. Greedy nearest-neighbour is a heuristic and is not
guaranteed to find the globally optimal travelling-salesperson route.
