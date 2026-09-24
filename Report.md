# Review of: Three Presentations on Geographical Analysis and Modeling: Non-Isotropic Geographic Modeling; Speculations on the Geometry of Geography; and Global Spatial Analysis (Tobler, 1993)

## 1. Introduction

The distance between two points on the Earth is often not as simple as the straight-line distance between their coordinates. The Earth is not a flat plane; it has bumps, peaks, and valleys. Tobler asks why we don't build geographical models around that fact rather than treating it as an inconvenience.

It costs to travel, whether it is gas, calories, or the price of a plane ticket. Geographic movement cost is not necessarily **isotropic**. Isotropic means the conditions are the same in every direction, so movement or distance behaves equally no matter which way you go. Imagine a smooth flat plane $1km \times 1km$. The cost to travel east would take the same amount of time as traveling north. But imagine we put a large mountain to the north. Our travel times would not be the same. Heading north, we would have to scale up and over a mountain. That takes a lot of energy.

So we ask: how does terrain-aware routing differ from shortest-distance routing? Here I use a real elevation raster, Tobler's hiking function, **Dijkstra's algorithm**, and a comparison against shortest-distance routing.

## 2. Background / Tobler's Model

This difference in travel cost depending on direction is the main idea behind Tobler’s non-isotropic geographic model. Rather than taking distance as having the same cost in every direction, Tobler takes into account factors such as terrain and slope. One of the ways he shows this is through his **hiking function**, which estimates speed based on the slope of the terrain.

$$v=6e^{-3.5|s+0.05|}$$

Where,

- $v =$ walking speed (in km/h)

- $s = \frac{rise}{run}$, i.e. slope

An important note is the $+0.05$. If you are on a slight decline, you are naturally going to move a bit faster. Tobler predicts maximum walking speed on a slight downhill of about a 5% grade.

## 3. Data

For the implementation, I used a Digital Elevation Model (DEM) from the USGS 3D Elevation Program (3DEP), downloaded using the `py3dep` Python library. The selected area covered the Ricketts Glen region of northeastern Pennsylvania.

<div align="center">

  <img src="./photo/IMG_3671.JPG" alt="see photo" width="50%">

</div>

The elevation data was stored as a GeoTIFF raster, where each cell represents the elevation of a small area of terrain.

The raster used for the main experiments contained 646 rows and 609 columns and used the EPSG:5070 projected coordinate reference system. Each raster cell was approximately $26.34m \times 26.34m$. Because the coordinate system is projected in meters, the physical distance between neighboring cells could be calculated directly. Horizontal and vertical neighbors were approximately $26.34m$ apart, while diagonal neighbors were approximately

$$\sqrt{26.34^2 + 26.34^2} \approx 37.25m$$

apart.

Each cell contained a single elevation value in meters. These elevation values were then used to calculate the change in elevation, or rise, between neighboring cells. Combined with the horizontal distance between cells, this allowed the slope of movement from one cell to another to be calculated.

The DEM was treated as the geographic environment for the routing experiments. Instead of using existing roads or hiking trails, movement was allowed directly across the raster. This made it possible to focus specifically on how elevation and slope influence route choice.

## 4. Methodology

### 4.1 Raster Graph Construction

### 4.2 Slope and Travel Cost

### 4.3 Pathfinding

## 5. Experiments

## 6. Results

## 7. Discussion

## 8. Limitations

## 9. Conclusion

## References

Tobler, W. (1993). Three Presentations on Geographical Analysis and Modeling: Non-Isotropic Geographic Modeling; Speculations on the Geometry of Geography; and Global Spatial Analysis (93-1). UC Santa Barbara: National Center for Geographic Information and Analysis. Retrieved from [https://escholarship.org/uc/item/05r820mz](https://escholarship.org/uc/item/05r820mz)