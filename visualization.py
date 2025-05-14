import matplotlib.pyplot as plt
from descartes import PolygonPatch

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

    ax.set_xlim(-5, 20)
    ax.set_ylim(-5, 20)
    ax.set_aspect('equal')
    plt.show()

# Define the area (e.g., an irregular polygon)
area = Polygon([(0, 0), (10, 0), (8, 8), (2, 10), (0, 5)])

grid = SensorGrid(area)
grid.add_sensor(Sensor(3, 4, 2))
grid.add_sensor(Sensor(7, 2, 3))
grid.add_sensor(Sensor(15, 5, 2))  # Will print a warning

print(f"Covered area: {grid.covered_area().area}")
print(f"Uncovered area: {grid.uncovered_area().area}")


plot_grid(grid)
