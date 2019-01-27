
"""Default cell size in grid."""
CELL_SIZE = 85

"""Minimum cell size in grid when zoom."""
MIN_CELL_SIZE = 75

"""Minimum cell size in grid when zoom."""
MAX_CELL_SIZE = 100

"""One step when turn the mouse wheel."""
ZOOM_CELL_STEP = 2

"""One tick in game. Discrete time. With low tick can simulate continual time theoretical."""
TICK_TIME = 0.17

"""Specifies how large the images from the SVG format will be rendered in pixels. 
Higher resolution may slow down the game."""
RENDER_RECT_SIZE = 500

"""Initial map size. It does not matter much because the map is endless and can be moved freely."""
START_MAP_SIZE = 50

"""Constants for generate bullets on map, with a greater distance from the start, their numbers are greatly reduced.

According to the following formula (distance is Euclidean distance from start):
p = min(BULLETS_MAX_PROB, (1/(distance^BULLETS_EXPONENT))*BULLETS_MULTIPLY)
Constants bellow can be change to manage difficulty.

The exponent specifies how quickly the difficulty will deteriorate.
The multiply constants do the linear scaling.
The max specifies the maximum on the start. Avoid all neighbors are bullets.
"""
BULLETS_EXPONENT = 1.4
BULLETS_MULTIPLY = 3
BULLETS_MAX_PROB = 0.05

"""Constants for generate healths on map, with a greater distance from the start, their numbers are greatly reduced.

According to the following formula (distance is Euclidean distance from start):
p = min(HEALTH_MAX_PROB, (1/(distance^HEALTH_EXPONENT))*HEALTH_MULTIPLY)
Constants bellow can be change to manage difficulty.

The exponent specifies how quickly the difficulty will deteriorate.
The multiply constants do the linear scaling.
The max specifies the maximum on the start. Avoid all neighbors are healths.
"""
HEALTH_EXPONENT = 1.4
HEALTH_MULTIPLY = 1
HEALTH_MAX_PROB = 0.01

"""Constants for generate enemy on map, with a greater distance from the start, their number increases.

According to the following formula (distance is Euclidean distance from start):
p = min(ENEMY_MAX_PROB, ENEMY_START_PROBABILITY * (distance/ENEMY_DISTANCE_DIVIDER))
Constants bellow can be change to manage difficulty.

The distance divider uses to decrease the computed Euclidean distance from start to moderate difficulty increasing.
The start probability constants add the scale to the valnted value.
The max specifies the maximum. Avoid all fields are occupied by enemies.
"""
ENEMY_START_PROBABILITY = 0.01
ENEMY_DISTANCE_DIVIDER = 10
ENEMY_MAX_PROB = 0.05

"""Constants for generate guns on map, with a greater distance from the start, their numbers are greatly reduced.

According to the following formula (distance is Euclidean distance from start):
p = min(GUNS_MAX_PROB, (1/(distance^GUNS_EXPONENT))*GUNS_MULTIPLY)
Constants bellow can be change to manage difficulty.

The exponent specifies how quickly the difficulty will deteriorate.
The multiply constants do the linear scaling.
The max specifies the maximum on the start. Avoid all neighbors are guns.
"""
GUNS_EXPONENT = 1.4
GUNS_MULTIPLY = 1
GUNS_MAX_PROB = 0.01
