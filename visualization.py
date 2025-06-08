import matplotlib.pyplot as plt

from project_classes import Sensor, SensorGrid
from shapely.geometry import Polygon

import matplotlib.pyplot as plt

from solve import epsilon_objective, ws_objective

import numpy as np

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

# area = Polygon([(0, 0), (10, 0), (8, 8), (2, 10), (0, 5)])

# New York City area polygon (km)
area_ny = Polygon([
    (0.0, 0.0), (5.0, -0.5), (10.0, 0.0), (13.0, 3.0), (14.0, 8.0),
    (13.5, 12.0), (12.0, 17.0), (10.0, 22.0), (7.0, 27.0),
    (4.0, 30.0), (2.0, 28.0), (1.0, 25.0), (0.5, 20.0), (0.0, 15.0)
])

area_lac = Polygon([
    (2, 75),
    (18, 40),
    (15, 30),
    (0, 13),
    (38, 0),
    (48, 4),
    (55, 13),
    (65, 13),
    (72, 40),
    (75, 75)
])

area_kz = Polygon([
    (0, 1),
    (4.5, 1),
    (4.5, 0),
    (5, 0),
    (5, 1),
    (6, 1),
    (6, 3),
    (4.5, 3),
    (4.5, 6),
    (6, 7.2),
    (5.5, 8),
    (4, 7),
    (2.5, 7),
    (2.5, 5),
    (.7, 5),
    (.7, 7),
    (0, 7)
])

area = area_kz

k = 3
d = 0.6
delta = 0
t = (0, 0)
range = 0.9
shape = "Hexagonal"  # "Square" or "Hexagonal"

resolution = 50  # Resolution for area calculations

grid = SensorGrid(area, base_range=range)

grid.create_hexagonal_grid(d=d, delta=delta, t=t, k=k)

print(f"Number of sensors: {len(grid.sensors)}")
print(f"Missed sensors: {grid.missed_sensors}")

print(f"Percentage of covered area: {grid.covered_area().area / grid.area.area * 100:.2f}%")
# print(f"Percentage of k-covered area (k = 2): {grid.k_covered_area(2, resolution=resolution) / grid.area.area * 100:.2f}%")

f2 = grid.k_uncovered_area(3, resolution=resolution) / grid.area.area
print(f"Percentage of k-uncovered area (k = 3): {f2 * 100:.4f}%")


ideal_sensors = area.area / (range ** 2 * np.pi) * k
f1 = grid.number_of_sensors() / ideal_sensors

print(f"F1 score: {f1:.4f}")

print(f"WS score: {0.8 * f2 + 0.2 * f1:.4f}")
print(f"Epsilon score: {epsilon_objective((d, delta, t[0], t[1]), area, k, resolution, eps=0.95, shape=shape, ideal_sensors=ideal_sensors, penalty=True, sensor_range=range):.4f}")
plot_grid(grid)
