## TSUNAMI EVACUATION ROUTE PLANNER
Finds the nearest safe place to evacuate to during a tsunami, plus a backup option, using a modified version of Dijkstra's algorithm.

A place is safe if it is at least 20 m above sea level and not flooded.

### Features
Choose a starting location and transport method (car, bicycle or walking)
Mark places as flooded: routes can't enter or end at them
Mark roads as closed: they are removed in both directions
Shows the nearest safe place and an alternative, with distance, travel time and route

### How it works
1. Start at the chosen location with distance 0.
2. Repeatedly take the nearest unchecked place.
3. If it's safe, stop and trace the route back to the start.
4. Otherwise, add its non-flooded neighbours, keeping only the shortest route to each.
