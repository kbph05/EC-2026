# SFU ESSS Engineering Competition 2026 

This is a skeleton front end with a mock data set for the 2026 SFU Engineering Competition. It uses React.js and TypeScript for React.js. Feel free to modify it as you wish; as long as all the requirements are included, the judges will not be picky about it.

## Layout

```
src/
  assets/evacuation-map.jpeg   the provided map
  components/                  EvacuationMap, MapData, StatusBanner
  data/
    GraphData.tsx               points A-P, junctions J1-J4, roads and distances
    ElevationData.tsx           elevation of each point, safe elevation (20 m)
    Scenarios.tsx               tsunami and road-closure scenarios
    Assumptions.tsx             walking and driving speeds
  simulation/types.tsx          shared types
```

## Things to know

- **Distances are unitless.** Use the numbers on the roads. Travel time is
  distance / speed.
- **J1-J4 are junctions and not points.** which are where roads intersect each other on the map
  and are never destinations. Check `isRefuge` in `GraphData.tsx`.
- **Roads are bi-directional.** Each road has an id such as `"C-E"`. Scenarios close a
  road by listing its id in `closedRoads`.
- **All data here is illustrative**, not real survey or tsunami-model data.
  Be ready to explain the data sources you use.
- A safe point is safe only if its elevation is at least `SAFE_ELEVATION_METRES`
  and it is not inside the active hazard zone.


## Dependencies

To build you must have the following:

Node.js
```bash
npm install
```

## Getting started:

Clone the repository and navigate to the `Tsunami-Evacuation-Map` directory:
```bash
git clone 
cd Tsunami-Evacuation-Map
```

## Testing

To run the app:
```bash
cd Tsunami-Evacuation-Map
npm run dev 
```
and then type `localhost:5173` in your browser