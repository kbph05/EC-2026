

from classes import Edge, Node
import heapq



SAFE_ELEVATION_METRES = 20
elevations: dict[str, float] = {
        "A": 45, "B": 12, "C": 60, "D": 35, "E": 55, "F": 18, "G": 70, "H": 40,
        "I": 5, "J": 8, "K": 50, "L": 25, "M": 15, "N": 4, "O": 6, "P": 3, "J1": 0, "J2": 0, "J3": 0, "J4": 0
    }

roads: list[tuple[str, str, float]] = [
        # Western spine
        ("A", "J1", 1),
        ("J1", "B", 0.5),
        ("J1", "C", 2),
        ("B", "C", 1.5),
        ("C", "D", 0.5),
        ("C", "E", 1),
        ("E", "G", 4),
        ("G", "K", 5),

        ("D", "J2", 3),
        ("J2", "J3", 2),
        ("J3", "J4", 4),

        ("E", "J2", 2),
        ("J2", "F", 1),

        ("G", "J3", 2),
        ("J3", "H", 1),

        ("F", "H", 2),
        ("H", "L", 5),

        ("I", "G", 3),
        ("I", "J", 6),
        ("G", "J", 6.5),
        ("J", "K", 3),

        ("K", "J4", 2),
        ("J4", "L", 1),

        ("L", "M", 4),
        ("L", "N", 3),
        ("L", "O", 4),
        ("M", "O", 3),
        ("N", "O", 2),
        ("N", "P", 4),
        ("O", "P", 2),
    ]

def nearest_safe_node(nodes, start, not_a_stop=[]):
    """
    Returns the nearest safe node to the given node based on elevation.
    Uses Dijkstra's algorithm to find the shortest path to a safe node.
    If no safe nodes are found, it returns None.
    """
    
    distance_to = {start: 0}      # shortest distance found to each place
    came_from = {}                # which place we came from to get there
    to_visit = [(0, start)]       # places waiting to be checked, as (distance, name)

    while to_visit:
        # closest place we haven't checked yet
        distance, name = heapq.heappop(to_visit)

        # Is it safe and not overcrowded? If so, complete! Then trace the route back to the start
        if name not in not_a_stop and nodes[name].enabled and nodes[name].elevation >= SAFE_ELEVATION_METRES:
            route = [name]
            while route[-1] != start:
                route.append(came_from[route[-1]])
            route.reverse()
            return name, distance, route

        # Otherwise, look at every road from the node
        for road in nodes[name].edges:

            # name of the node at the other end of the road
            neighbour = road.dst.name

            # Total distance to get to the neighbour from the start
            new_distance = distance + road.weight

            # Only keep it if the neighbour is safe AND this way is shorter than any we've found, infinity if we haven't found any way yet
            if road.dst.enabled and new_distance < distance_to.get(neighbour, float("inf")):
                distance_to[neighbour] = new_distance
                came_from[neighbour] = name
                heapq.heappush(to_visit, (new_distance, neighbour))

    return None   # ran out of places to check: no safe place reachable



def find_route(starting_node, transport, flooded, closed, not_a_stop=[], changed_weights=None):
    if changed_weights is None:
        changed_weights = {}
    
    
    Transportation_Mult = {
        "Car": 1.0,
        "Bicycle": 0.5,
        "Walk": 0.3,
        "Walking with A Child": 0.2,
        "Wheelchair": 0.1,
        "Wheelchair (stolen)": 0.05
    }

    

    nodes: dict[str, Node] = {name: Node(name, elevation, True) for name, elevation in elevations.items()}

    for src, dst, weight in roads:

        # Update the weight if it has been changed from input check either direction, otherwise use the default weight
        weight = changed_weights.get(f"{src}-{dst}", changed_weights.get(f"{dst}-{src}", weight))
        a = nodes[src]
        b = nodes[dst]
        forward = Edge(f"{src}-{dst}", weight, a, b)
        backward = Edge(f"{dst}-{src}", weight, b, a)
        if f"{src}-{dst}" in closed or f"{dst}-{src}" in closed:
            continue  # skip adding this edge if it's closed
        a.edges.append(forward)
        b.edges.append(backward)
        
    for name in flooded:
        nodes[name].enabled = False

    result = nearest_safe_node(nodes, starting_node, not_a_stop=not_a_stop)

    if result is None:
        return None     # no safe place at all

    name, distance, route = result
    best = {
        "name": name,
        "distance": distance,
        "time": round(distance / Transportation_Mult.get(transport, 1.0), 2),
        "route": route,
        "desination_elevation": nodes[name].elevation
    }

    return best