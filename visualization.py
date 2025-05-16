import matplotlib.pyplot as plt

from project_classes import Sensor, SensorGrid
from shapely.geometry import Polygon

import matplotlib.pyplot as plt

def plot_polygon(ax, polygon, color='lightgrey', alpha=0.5, edgecolor='black'):
    x, y = polygon.exterior.xy
    ax.fill(x, y, facecolor=color, edgecolor=edgecolor, alpha=alpha)

def plot_grid(grid: SensorGrid):
    fig, ax = plt.subplots()

    # Plot the area polygon
    plot_polygon(ax, grid.area)

    # Plot each sensor and its coverage
    for sensor in grid.sensors:
        coverage = sensor.coverage_area
        if hasattr(coverage, "geoms"):  # MultiPolygon
            for geom in coverage.geoms:
                plot_polygon(ax, geom, color='blue', alpha=0.3)
        else:
            plot_polygon(ax, coverage, color='blue', alpha=0.3)

        ax.plot(sensor.position.x, sensor.position.y, 'bo')

    # ax.set_xlim(-5, 20)
    # ax.set_ylim(-5, 20)
    ax.set_aspect('equal')
    plt.show()

# Define the area (e.g., an irregular polygon)
area = Polygon([(0, 0), (10, 0), (8, 8), (2, 10), (0, 5)])

k = 3
d = 2
delta = 0
t = (0, 0)
range = 1.5

grid = SensorGrid(area, base_range=range)
grid.create_hexagonal_grid(d=d, delta=delta, t=t)

print(f"Number of sensors: {len(grid.sensors)}")
print(f"Missed sensors: {grid.missed_sensors}")

print(f"Covered area: {grid.covered_area().area}")
print(f"Percentage of covered area: {grid.covered_area().area / grid.area.area * 100:.2f}%")
print(f"Uncovered area: {grid.uncovered_area().area}")

print(f"Percentage of k-covered area (k = {k}): {grid.k_covered_area(k) / grid.area.area * 100:.2f}%")

plot_grid(grid)
