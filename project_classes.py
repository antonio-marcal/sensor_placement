from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

class Sensor:
    def __init__(self, x, y, radius):
        self.position = Point(x, y)
        self.radius = radius
        self.coverage_area = self.position.buffer(radius)

    def __repr__(self):
        return f"Sensor(x={self.position.x}, y={self.position.y}, r={self.radius})"

class SensorGrid:
    def __init__(self, area_polygon: Polygon):
        self.area = area_polygon
        self.sensors = []

    def add_sensor(self, sensor: Sensor):
        if sensor.position.within(self.area):
            self.sensors.append(sensor)
        else:
            print(f"Warning: Sensor at {sensor.position} is outside the area.")

    def covered_area(self):
        raw_union = unary_union([s.coverage_area for s in self.sensors])
        return raw_union.intersection(self.area)


    def uncovered_area(self):
        """Return the part of the area not covered by any sensor"""
        return self.area.difference(self.covered_area())
