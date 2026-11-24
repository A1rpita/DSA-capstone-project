import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Smart Delivery Route Optimizer", page_icon="🚚", layout="wide")

# Road network: edge weights represent distance in kilometres.
COORDS = {
    "Depot": (0, 0), "A": (2, 1), "B": (4, 0), "C": (6, 2),
    "D": (2, 4), "E": (5, 5), "F": (8, 4), "G": (9, 0)
}
ROADS = [
    ("Depot", "A", 3), ("Depot", "D", 5), ("A", "B", 3),
    ("A", "D", 3), ("B", "C", 3), ("B", "G", 6),
    ("C", "E", 4), ("C", "F", 3), ("D", "E", 4),
    ("E", "F", 3), ("F", "G", 5), ("B", "E", 5),
    ("A", "C", 6), ("D", "B", 4)
]

def build_graph():
    graph = nx.Graph()
    for node, pos in COORDS.items():
        graph.add_node(node, pos=pos)
    for u, v, distance in ROADS:
        graph.add_edge(u, v, weight=distance)
    return graph

def shortest_path(graph, source, target):
    path = nx.dijkstra_path(graph, source, target, weight="weight")
    distance = nx.dijkstra_path_length(graph, source, target, weight="weight")
    return path, distance

def optimize_route(graph, depot, stops):
    """Greedy nearest-neighbour scheduling using shortest-road distances."""
    remaining = set(stops)
    current = depot
    order = [depot]
    total_distance = 0
    legs = []
    while remaining:
        next_stop = min(
            remaining,
            key=lambda stop: nx.shortest_path_length(
                graph, current, stop, weight="weight"
            )
        )
        path, distance = shortest_path(graph, current, next_stop)
        legs.append({"From": current, "To": next_stop,
                     "Road path": " → ".join(path), "Distance (km)": distance})
        order.extend(path[1:])
        total_distance += distance
        current = next_stop
        remaining.remove(next_stop)
    return order, total_distance, legs

def route_distance(graph, route):
    total = 0
    for a, b in zip(route, route[1:]):
        total += nx.shortest_path_length(graph, a, b, weight="weight")
    return total

def draw_network(graph, route, delivery_stops):
    pos = nx.get_node_attributes(graph, "pos")
    fig, ax = plt.subplots(figsize=(10, 6))
    nx.draw_networkx_edges(graph, pos, ax=ax, edge_color="#aab4c0", width=2)
    nx.draw_networkx_nodes(graph, pos, nodelist=list(graph.nodes),
                           node_color="#dbeafe", node_size=1000,
                           edgecolors="#2563eb", linewidths=1.5, ax=ax)
    nx.draw_networkx_nodes(graph, pos, nodelist=["Depot"], node_color="#16a34a",
                           node_size=1200, ax=ax)
    if delivery_stops:
        nx.draw_networkx_nodes(graph, pos, nodelist=delivery_stops,
                               node_color="#fbbf24", node_size=1000, ax=ax)
    nx.draw_networkx_labels(graph, pos, font_size=10, font_weight="bold", ax=ax)
    edge_labels = nx.get_edge_attributes(graph, "weight")
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels,
                                 font_size=8, ax=ax)
    # Draw each optimized shortest-path leg in route order.
    for u, v in zip(route, route[1:]):
        if graph.has_edge(u, v):
            nx.draw_networkx_edges(graph, pos, edgelist=[(u, v)],
                                   edge_color="#dc2626", width=3.5, ax=ax)
    ax.set_title("Road Network and Optimized Delivery Route", fontsize=14)
    ax.axis("off")
    fig.tight_layout()
    return fig

st.title("🚚 Smart Delivery Route Optimization System")
st.caption("Graph theory • Dijkstra shortest paths • Greedy scheduling • Route analytics")

G = build_graph()
all_locations = [n for n in G.nodes if n != "Depot"]

with st.sidebar:
    st.header("Delivery settings")
    selected = st.multiselect(
        "Select delivery locations",
        all_locations,
        default=["A", "C", "E", "G"]
    )
    speed = st.number_input("Average vehicle speed (km/hour)", min_value=5,
                            max_value=100, value=30, step=5)
    service_time = st.number_input("Service time per delivery (minutes)",
                                   min_value=0, max_value=60, value=5, step=1)
    st.info("The green node is the depot. Yellow nodes are selected delivery stops. Red edges show the optimized route.")

if not selected:
    st.warning("Select at least one delivery location to calculate a route.")
    st.stop()

route, total_km, legs = optimize_route(G, "Depot", selected)
travel_minutes = (total_km / speed) * 60
service_minutes = len(selected) * service_time
total_minutes = travel_minutes + service_minutes

# A simple reference route uses the selected locations in alphabetical order.
reference_order = ["Depot"] + sorted(selected)
reference_km = route_distance(G, reference_order)
saving = reference_km - total_km
saving_pct = (saving / reference_km * 100) if reference_km else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Optimized distance", f"{total_km:.1f} km")
c2.metric("Estimated total time", f"{total_minutes:.0f} min")
c3.metric("Delivery stops", str(len(selected)))
c4.metric("Distance saved vs. reference", f"{saving:.1f} km", f"{saving_pct:.1f}%")

left, right = st.columns([1.5, 1])
with left:
    st.subheader("Optimized route map")
    st.pyplot(draw_network(G, route, selected), use_container_width=True)
with right:
    st.subheader("Delivery sequence")
    sequence = ["Depot"] + selected
    st.write(" → ".join(sequence))
    st.caption("Each leg is calculated using the shortest road path.")
    st.dataframe(pd.DataFrame(legs), use_container_width=True, hide_index=True)

st.subheader("Performance analysis")
p1, p2 = st.columns(2)
with p1:
    st.write("**Distance comparison**")
    comparison = pd.DataFrame({
        "Route": ["Alphabetical reference", "Greedy optimized"],
        "Distance (km)": [reference_km, total_km]
    }).set_index("Route")
    st.bar_chart(comparison)
with p2:
    st.write("**Estimated time breakdown**")
    timing = pd.DataFrame({
        "Activity": ["Driving", "Delivery service"],
        "Minutes": [travel_minutes, service_minutes]
    }).set_index("Activity")
    st.bar_chart(timing)

st.subheader("Algorithm details")
st.markdown("""
- **Graph model:** Each location is a vertex; each road is an undirected weighted edge.
- **Shortest path:** Dijkstra's algorithm finds the minimum-distance road path between two locations.
- **Scheduling:** Greedy nearest-neighbour chooses the unvisited delivery stop with the smallest shortest-path distance from the current location.
- **Time estimate:** Driving time is total distance divided by average speed; service time is added for every delivery.
""")
st.warning("This is a simulation using sample road distances, not live traffic or GPS data. The greedy method is a heuristic and does not guarantee the globally shortest multi-stop tour.")
