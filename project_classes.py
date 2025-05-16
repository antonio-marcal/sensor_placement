from shapely.geometry import Point, Polygon, MultiPoint
from shapely.ops import unary_union

import numpy as np
import math


class Sensor:
    def __init__(self, x, y, radius):
        self.position = Point(x, y)
        self.radius = radius
        self.coverage_area = self.position.buffer(radius)

    def __repr__(self):
        return f"Sensor(x={self.position.x}, y={self.position.y}, r={self.radius})"

class SensorGrid:
    def __init__(self, area_polygon: Polygon, base_range: float = 0):
        self.area = area_polygon
        self.base_range = base_range
        self.missed_sensors = 0
        self.sensors = []

    def add_sensor(self, sensor: Sensor):
        if sensor.position.within(self.area):
            self.sensors.append(sensor)
        else:
            self.missed_sensors += 1

    def create_square_grid(self, d: float, delta: float = 0, t: tuple = (0, 0)):
        """
        Create a square grid of sensors within the area.
        
        Parameters:
        d (float): Distance between sensors.
        delta (float): Rotation of the grid.
        t (tuple): Translation of the grid.
        """
        # Calculate the bounding box of the area
        min_x, min_y, max_x, max_y = self.area.bounds

        # Adjust to keep sensors from levaing blank spots when rotating
        min_x -= (max_x - min_x) * 0.2
        min_y -= (max_y - min_y) * 0.2
        max_x += (max_x - min_x) * 0.2
        max_y += (max_y - min_y) * 0.2

        # Compute the center of the area
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2

        # Create a grid of points
        x_coords = [min_x + i * d for i in range(int((max_x - min_x) / d) + 1)]
        y_coords = [min_y + j * d for j in range(int((max_y - min_y) / d) + 1)]

        delta = math.radians(delta)
        cos_theta = math.cos(delta)
        sin_theta = math.sin(delta)

        # Add sensors to the grid
        for x in x_coords:
            for y in y_coords:

                # Translate to origin for rotation
                x_shifted = x - center_x
                y_shifted = y - center_y

                # Rotate around the centre
                x_rot = x_shifted * cos_theta - y_shifted * sin_theta
                y_rot = x_shifted * sin_theta + y_shifted * cos_theta

                sensor = Sensor(x_rot + center_x + t[0], y_rot + center_y + t[1], self.base_range)
                self.add_sensor(sensor)

    def create_hexagonal_grid(self, d: float, delta: float = 0, t: tuple = (0, 0), k: int = 1):
        """
        Create a triangular-based hexagonal grid of sensors.

        Parameters:
        d (float): Side length of equilateral triangles.
        delta (float): Rotation of the grid.
        t (tuple): Translation of the grid.
        k (int): Number of sensors per hexagonal region.
        """
        # Bounding box
        min_x, min_y, max_x, max_y = self.area.bounds
        width = max_x - min_x
        height = max_y - min_y

        # Height of equilateral triangle
        tri_height = d * math.sqrt(3) / 2

        # Loop through rows and columns to generate triangle grid
        row = 0
        y = min_y
        while y < max_y:
            x_offset = 0 if row % 2 == 0 else d / 2
            x = min_x
            while x < max_x:
                # Create upright triangle
                p1 = (x + x_offset, y)
                p2 = (x + x_offset + d / 2, y + tri_height)
                p3 = (x + x_offset + d, y)
                triangle = Polygon([p1, p2, p3])
                if self.area.intersects(triangle):
                    self.add_sensor(Sensor(*triangle.centroid.coords[0], self.base_range))

                # Create upside-down triangle
                p1_down = (x + x_offset + d / 2, y + tri_height)
                p2_down = (x + x_offset + d, y + 2 * tri_height)
                p3_down = (x + x_offset, y + 2 * tri_height)
                triangle_down = Polygon([p1_down, p2_down, p3_down])
                if self.area.intersects(triangle_down):
                    self.add_sensor(Sensor(*triangle_down.centroid.coords[0], self.base_range))

                x += d

            y += tri_height
            row += 1
    

    def covered_area(self):
        raw_union = unary_union([s.coverage_area for s in self.sensors])
        return raw_union.intersection(self.area)

    def k_covered_area(self, k, resolution=10):
        """
        Fast version: Return area (float) covered by at least k sensors, restricted to main area.
        Error margins around 4/5% with resolution=10.
        Error margins around 0.3/0.4% with resolution=100.
        """
        if k <= 1:
            return self.covered_area().intersection(self.area)

        # Step 1: Generate grid
        minx, miny, maxx, maxy = self.area.bounds
        width = int((maxx - minx) * resolution)
        height = int((maxy - miny) * resolution)

        # Grid coordinates
        x = np.linspace(minx, maxx, width)
        y = np.linspace(miny, maxy, height)
        xx, yy = np.meshgrid(x, y)
        grid_points = np.column_stack((xx.ravel(), yy.ravel()))

        # Step 2: Precompute area mask
        area_mask = np.array([self.area.contains(Point(pt)) for pt in grid_points], dtype=bool)
        area_mask = area_mask.reshape((height, width))

        # Step 3: Count sensor coverage using distance math
        coverage_grid = np.zeros((height, width), dtype=np.uint8)

        for sensor in self.sensors:
            sx, sy = sensor.position.x, sensor.position.y
            radius = sensor.radius

            # Use vectorized distance check (x - sx)^2 + (y - sy)^2 <= r^2
            distance_squared = (xx - sx) ** 2 + (yy - sy) ** 2
            covered = distance_squared <= radius ** 2

            coverage_grid += covered.astype(np.uint8)

        # Step 4: Apply masks
        covered_mask = (coverage_grid >= k) & area_mask
        cell_area = (1 / resolution) ** 2
        covered_area = covered_mask.sum() * cell_area

        return covered_area

    def uncovered_area(self):
        """Return the part of the area not covered by any sensor"""
        return self.area.difference(self.covered_area())
    
    def k_uncovered_area(self, k):
        """Return the part of the area not covered by at least k sensors"""
        return self.area.difference(self.k_covered_area(k))

    def number_of_sensors(self):
        return len(self.sensors)
