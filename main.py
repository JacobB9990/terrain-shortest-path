import rasterio
import math
import numpy as np
import heapq
import matplotlib.pyplot as plt

with rasterio.open("./data/ricketts_glen_dem.tif") as src:
    elevation = src.read(1)
    x_res, y_res = src.res


def calc_distance(row1, col1, row2, col2):
    row_diff = row2 - row1
    col_diff = col2 - col1

    dy = row_diff * y_res
    dx = col_diff * x_res

    distance = math.sqrt(dx**2 + dy**2)

    return distance


def calc_slope(row1, col1, row2, col2):
    first = elevation[row1][col1]
    second = elevation[row2][col2]

    rise = second - first
    run = calc_distance(row1, col1, row2, col2)

    slope = rise / run

    return slope


def calc_speed(s):
    absolute_val = abs(s + 0.05)
    power = -3.5 * absolute_val

    v = 6 * math.exp(power)

    return v


def calc_time(distance, speed):
    distance_km = distance / 1000

    return distance_km / speed


def get_neighbors(row, col):
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    neighbors = []

    for dr, dc in directions:
        new_row = row + dr
        new_col = col + dc

        if 0 <= new_row < elevation.shape[0] and 0 <= new_col < elevation.shape[1]:
            neighbors.append((new_row, new_col))

    return neighbors


def get_terrain_cost(row1, col1, row2, col2):
    distance = calc_distance(row1, col1, row2, col2)
    slope = calc_slope(row1, col1, row2, col2)
    speed = calc_speed(slope)
    time = calc_time(distance, speed)

    return time


def get_distance_cost(row1, col1, row2, col2):
    return calc_distance(row1, col1, row2, col2)


def compute_dijkstra(start, end, cost_function):
    distances = np.full(elevation.shape, np.inf)
    distances[start] = 0

    parents = {}

    queue = []
    heapq.heappush(queue, (0, start))

    while queue:
        current_cost, current = heapq.heappop(queue)

        row, col = current

        if current_cost > distances[row, col]:
            continue

        if current == end:
            break

        for neighbor in get_neighbors(row, col):
            nr, nc = neighbor

            move_cost = cost_function(row, col, nr, nc)

            new_cost = current_cost + move_cost

            if new_cost < distances[nr, nc]:
                distances[nr, nc] = new_cost
                parents[neighbor] = current

                heapq.heappush(queue, (new_cost, neighbor))

    return distances, parents


def reconstruct_path(parents, start, end):
    path = []
    current = end

    while current != start:
        path.append(current)

        if current not in parents:
            print("No path found.")
            return []

        current = parents[current]

    path.append(start)
    path.reverse()

    return path


def total_path_distance(path):
    total = 0

    for i in range(len(path) - 1):
        row1, col1 = path[i]
        row2, col2 = path[i + 1]

        total += calc_distance(row1, col1, row2, col2)

    return total


def total_path_time(path):
    total = 0

    for i in range(len(path) - 1):
        row1, col1 = path[i]
        row2, col2 = path[i + 1]

        total += get_terrain_cost(row1, col1, row2, col2)

    return total


def elevation_stats(path):
    gain = 0
    loss = 0

    for i in range(1, len(path)):
        row1, col1 = path[i - 1]
        row2, col2 = path[i]

        change = elevation[row2][col2] - elevation[row1][col1]

        if change > 0:
            gain += change
        else:
            loss += abs(change)

    return gain, loss


def get_elevation_profile(path):
    distances = [0.0]
    elevations = [elevation[path[0][0]][path[0][1]]]

    total_distance = 0

    for i in range(1, len(path)):
        row1, col1 = path[i - 1]
        row2, col2 = path[i]

        total_distance += calc_distance(row1, col1, row2, col2)

        distances.append(total_distance)
        elevations.append(elevation[row2][col2])

    return np.array(distances), np.array(elevations)


def save_or_show(save):
    if save:
        plt.savefig(save, dpi=130, bbox_inches="tight")
        plt.close()
    else:
        plt.show()


def plot_comparison(terrain_path, distance_path, start, end, save=None):
    terrain_rows = [cell[0] for cell in terrain_path]
    terrain_cols = [cell[1] for cell in terrain_path]

    distance_rows = [cell[0] for cell in distance_path]
    distance_cols = [cell[1] for cell in distance_path]

    plt.figure(figsize=(10, 8))

    plt.imshow(elevation, cmap="terrain")

    plt.colorbar(label="Elevation (m)")

    plt.plot(terrain_cols, terrain_rows, linewidth=2, label="Fastest Hiking Route")

    plt.plot(
        distance_cols,
        distance_rows,
        linewidth=2,
        linestyle="--",
        label="Shortest Distance Route",
    )

    plt.scatter(start[1], start[0], s=70, label="Start")

    plt.scatter(end[1], end[0], s=70, label="End")

    plt.title("Terrain-Aware vs Shortest-Distance Route")

    plt.xlabel("Column")
    plt.ylabel("Row")

    plt.legend()

    save_or_show(save)


def plot_elevation_profiles(terrain_path, distance_path, save=None):
    terrain_dist, terrain_elev = get_elevation_profile(terrain_path)

    shortest_dist, shortest_elev = get_elevation_profile(distance_path)

    plt.figure(figsize=(11, 6))

    plt.plot(terrain_dist / 1000, terrain_elev, label="Fastest Hiking Route")

    plt.plot(
        shortest_dist / 1000,
        shortest_elev,
        linestyle="--",
        label="Shortest Distance Route",
    )

    plt.xlabel("Distance Along Route (km)")
    plt.ylabel("Elevation (m)")
    plt.title("Route Elevation Profiles")

    plt.legend()
    plt.grid()

    save_or_show(save)


if __name__ == "__main__":
    # rows/cols for ricketts_glen_dem.tif (646x609)
    start = (477, 98) # default
    end = (371, 371) # default

    terrain_distances, terrain_parents = compute_dijkstra(start, end, get_terrain_cost)

    terrain_path = reconstruct_path(terrain_parents, start, end)

    distance_distances, distance_parents = compute_dijkstra(start, end, get_distance_cost)

    distance_path = reconstruct_path(distance_parents, start, end)

    terrain_distance = total_path_distance(terrain_path)

    terrain_time = total_path_time(terrain_path)

    shortest_distance = total_path_distance(distance_path)

    shortest_time = total_path_time(distance_path)

    terrain_gain, terrain_loss = elevation_stats(terrain_path)

    shortest_gain, shortest_loss = elevation_stats(distance_path)

    print("\n--- FASTEST HIKING ROUTE ---")
    print("Cells:", len(terrain_path))
    print("Distance:", terrain_distance / 1000, "km")
    print("Estimated time:", terrain_time * 60, "minutes")
    print("Elevation gain:", terrain_gain, "m")
    print("Elevation loss:", terrain_loss, "m")

    print("\n--- SHORTEST DISTANCE ROUTE ---")
    print("Cells:", len(distance_path))
    print("Distance:", shortest_distance / 1000, "km")
    print("Estimated hiking time:", shortest_time * 60, "minutes")
    print("Elevation gain:", shortest_gain, "m")
    print("Elevation loss:", shortest_loss, "m")

    print("\n--- DIFFERENCE ---")
    print(
        "Extra distance taken by terrain route:",
        terrain_distance - shortest_distance,
        "meters",
    )

    print("Time saved:", (shortest_time - terrain_time) * 60, "minutes")

    print("Elevation gain difference:", terrain_gain - shortest_gain, "meters")

    plot_comparison(terrain_path, distance_path, start, end)

    plot_elevation_profiles(terrain_path, distance_path)
