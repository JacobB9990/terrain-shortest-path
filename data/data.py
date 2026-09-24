import py3dep

# Ricketts Glen-ish region
# (west, south, east, north)
bbox = (-76.36, 41.27, -76.20, 41.40)

dem = py3dep.get_dem(bbox, resolution=10, crs=4326)

dem.rio.to_raster("./ricketts_glen_dem_superhigh.tif")

print(dem)
