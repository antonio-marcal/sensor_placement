# sensor_placement

solver.py computes the best values it can find for the decision variables. It uses different scoring systems according to the "STRATEGY" parameter. "WS" means Weighted Sum, "EPS" means Epsilon-Constraint, and "EPS_NL" means the constraints used are not linear.

visualization.py allows setting a specific value for the decision variables and seeing it overlapped with a specific area map, showing coverage visually and numerically according to various statistics.
