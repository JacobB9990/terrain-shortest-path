import rasterio
import matplotlib.pyplot as plt

with rasterio.open("./data/mount_washington_dem.tif") as src:
    elevation = src.read(1)

print(elevation.min())
print(elevation.max())
print(elevation.shape)

plt.imshow(elevation)
plt.colorbar(label="Elevation (m)")
plt.show()
