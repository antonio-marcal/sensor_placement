import numpy as np
import os
import csv

from shapely.geometry import Polygon
from scipy.optimize import differential_evolution
from multiprocessing import freeze_support

from project_classes import SensorGrid

# New York City area polygon (km)
area = Polygon([
    (0.0, 0.0), (5.0, -0.5), (10.0, 0.0), (13.0, 3.0), (14.0, 8.0),
    (13.5, 12.0), (12.0, 17.0), (10.0, 22.0), (7.0, 27.0),
    (4.0, 30.0), (2.0, 28.0), (1.0, 25.0), (0.5, 20.0), (0.0, 15.0)
])

SENSOR_RADIUS = 1.5
SENSOR_MIN_DISTANCE = 0.1
RESOLUTION = 10  # Resolution for area calculations
k = 3

ALPHA = 0.8   # Weight for uncovered area
BETA = 0.2   # Weight for number of sensors (ratio of ideal sensors)

EPS = 0.0368  # Epsilon value for epsilon-constraint  (max uncovered area allowed)

MAX_ITER = 30  # Maximum number of iterations for optimization
POP_SIZE = 10   # Population size for differential evolution

# Using the ideal sensors, since this helps keep the blance with alpha and beta regardless of the area size
ideal_sensors = area.area / (SENSOR_RADIUS ** 2 * np.pi) * k

def ws_objective(params, area, k, resolution, alpha, beta, shape = "Square"):
    d, delta_deg, tx, ty = params

    # With square grids, the value of t is parameterized with d
    if shape == "Square":
        tx *= d
        ty *= d

    grid = SensorGrid(area_polygon=area, base_range=SENSOR_RADIUS)

    if shape == "Square":
        grid.create_square_grid(d=d, delta=delta_deg, t=(tx, ty))
    elif shape == "Hexagonal":
        grid.create_hexagonal_grid(d=d, delta=delta_deg, t=(tx, ty), k=k)
    else:
        raise ValueError(f"Unknown shape: {shape}. Supported shapes are 'Square' and 'Hexagonal'.")

    total_area = area.area
    covered_area = grid.k_covered_area(k=k, resolution=resolution)
    uncovered_area = total_area - covered_area
    num_sensors = grid.number_of_sensors()

    cost = alpha * (uncovered_area / total_area ) + beta * (num_sensors / ideal_sensors)
    return cost

def epsilon_objective(params, area, k, resolution, shape="Square", eps=0.9, ideal_sensors=None):

    d, delta_deg, tx, ty = params

    # With square grids, the value of t is parameterized with d
    if shape == "Square":
        tx *= d
        ty *= d

    grid = SensorGrid(area_polygon=area, base_range=SENSOR_RADIUS)

    if shape == "Square":
        grid.create_square_grid(d=d, delta=delta_deg, t=(tx, ty))
    elif shape == "Hexagonal":
        grid.create_hexagonal_grid(d=d, delta=delta_deg, t=(tx, ty), k=k)
    else:
        raise ValueError(f"Unknown shape: {shape}. Supported shapes are 'Square' and 'Hexagonal'.")

    total_area = area.area
    covered_area = grid.k_covered_area(k=k, resolution=resolution)
    uncovered_area = total_area - covered_area
    num_sensors = grid.number_of_sensors()

    if uncovered_area / total_area > EPS:
        return 1e6  # Large penalty for infeasible solutions

    return num_sensors / ideal_sensors
   

def log_to_csv(d, delta, tx, ty, uncovered_area, num_sensors, cost, max_iter, resolution, alpha, beta, popsize, filename='optimization_log.csv'):
    file_exists = os.path.isfile(filename)
    
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header if file doesn't exist
        if not file_exists:
            writer.writerow([
                'd', 'delta', 'tx', 'ty', 'uncovered_area', 'num_sensors',
                'cost', 'max_iter', 'resolution', 'alpha', 'beta', 'popsize'
            ])
        
        # Write data row
        writer.writerow([
            round(d, 4), round(delta, 2), round(tx, 4), round(ty, 4),
            round(uncovered_area, 4), num_sensors,
            round(cost, 4), max_iter, resolution, alpha, beta, popsize
        ])
        
iteration_counter = 0
def counter_callback(xk, convergence):
    global iteration_counter
    iteration_counter += 1
    print(f"[Generation {iteration_counter}] Best solution so far: {xk}, convergence: {convergence:.6f}")
    
    return False

bounds_square = [
    (SENSOR_MIN_DISTANCE, SENSOR_RADIUS),  # d
    (0, 90),                                   # delta (degrees)
    (0, 1),   # t_x
    (0, 1),   # t_y
]

bounds_hexagon = [
    (SENSOR_MIN_DISTANCE, 2 * SENSOR_RADIUS / 3),  # d
    (0, 180),                                      # delta (degrees)
    (0, SENSOR_RADIUS),   # t_x
    (0, SENSOR_RADIUS),   # t_y
]

def main(shape, strat = 'WS'):

    bounds = bounds_square if shape == "Square" else bounds_hexagon

    if strat == 'WS':
        result = differential_evolution(
            ws_objective,
            bounds,
            args=(area, k, RESOLUTION, ALPHA, BETA, shape),
            strategy='best1bin',
            maxiter=MAX_ITER,
            popsize=POP_SIZE,
            tol=1e-3,
            # callback=counter_callback,
            disp=True,
            seed=48,
            updating='deferred',
            workers=-1  # Use all CPU cores if available
        )
    elif strat == 'EPS':

        result = differential_evolution(
            epsilon_objective,
            bounds,
            args=(area, k, RESOLUTION, shape, EPS, ideal_sensors),
            strategy='best1bin',
            maxiter=MAX_ITER,
            popsize=POP_SIZE,
            tol=1e-3,
            seed=48,
            disp=True,
            updating='deferred',
            workers=-1
        )


    best_d, best_delta, best_tx, best_ty = result.x
    best_tx = best_tx * best_d if shape == "Square" else best_tx
    best_ty = best_ty * best_d if shape == "Square" else best_ty

    print(f"Optimal d: {best_d:.4f}")
    print(f"Optimal delta: {best_delta:.2f}°")
    print(f"Optimal translation: ({best_tx:.4f}, {best_ty:.4f})")
    print(f"Objective value: {result.fun:.4f}")

    best_area = SensorGrid(area_polygon=area, base_range=SENSOR_RADIUS)
    if shape == "Square":
        best_area.create_square_grid(d=best_d, delta=best_delta, t=(best_tx, best_ty))
    elif shape == "Hexagonal":
        best_area.create_hexagonal_grid(d=best_d, delta=best_delta, t=(best_tx, best_ty), k=k)



    log_to_csv(
        d=best_d,
        delta=best_delta,
        tx=best_tx,
        ty=best_ty,
        uncovered_area=best_area.k_uncovered_area(k=k)/ best_area.area.area,
        num_sensors=best_area.number_of_sensors(),
        cost=result.fun,
        max_iter=MAX_ITER,
        resolution=RESOLUTION,
        alpha=ALPHA,
        beta=BETA,
        popsize=POP_SIZE
    )


if __name__ == '__main__':
    freeze_support()
    main("Square", "EPS")