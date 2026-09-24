import rasterio
import matplotlib.pyplot as plt

with rasterio.open("./data/ricketts_glen_dem_high.tif") as src:
    elevation = src.read(1)

print(elevation.min())
print(elevation.max())
print(elevation.shape)

plt.imshow(elevation)
plt.colorbar(label="Elevation (m)")
plt.show()
