
CELL_SIZE = 70
"""Default cell size in grid."""

MIN_CELL_SIZE = 50
"""Minimum cell size in grid when zoom."""

MAX_CELL_SIZE = 90
"""Minimum cell size in grid when zoom."""

ZOOM_CELL_STEP = 2
"""One step when turn the mouse wheel."""

TICK_TIME = 0.07
"""One tick in game. Discrete time. With low tick can simulate continual time theoretical."""

RENDER_RECT_SIZE = 700
"""Specifies how large the images from the SVG format will be rendered in pixels. 
Higher resolution may slow down the game."""

START_MAP_SIZE = 50
"""Initial map size. It does not matter much because the map is endless and can be moved freely."""

VIEW_RANGE = 6
"""How far a character sees."""

CHECK_RANGE = 40
"""How far is do the game play. AI move, and do all checks"""

HOW_FAR_SEE_AI = 3
"""What is the view range of AI enemies. 1 easy the dont see far, but with the same as VIEW_RANGE it is hard."""

LEVEL_1_AI_SIGHT = 2
"""View range of enemy on level 1"""

LEVEL_1_AI_FAST = 9
"""Time section between AI action for level 1. 0-9. 9 -> slow. 0 -> fast as possible."""

LEVEL_2_AI_SIGHT = 4
"""View range of enemy on level 2"""

LEVEL_2_AI_FAST = 6
"""Time section between AI action for level 2. 0-9. 9 -> slow. 0 -> fast as possible."""

LEVEL_3_AI_SIGHT = 6
"""View range of enemy on level 3"""

LEVEL_3_AI_FAST = 3
"""Time section between AI action for level 3. 0-9. 9 -> slow. 0 -> fast as possible."""

HOW_LONG_BETWEEN_TURN_AI = 5
"""Haw fast will be the AI. Maximum is 9 for very slow and 0 for fast AI."""

GO_FOR_PLAYER_AI_PROB = 0.1 # systematic find and to this direction
"""Probability of go for player. Select direction to player."""

GO_FOR_GUN_AI_PROB = 0.05 # if in near is gun catch it
"""Probability of go for nearest gun."""

GO_FOR_HEALTH_AI_PROB = 0.9 # if in near is health catch it, if need
"""Probability of go for nearest health."""

GO_FOR_BULLETS_AI_PROB = 0.1 # if in near is bullets catch it, if need
"""Probability of go for nearest bullets."""

START_GAME_TEXT = "PRESS ENTER TO START"
"""Text show on start the game."""

"""Texts in status bar."""
SCORE_TEXT = "Score"
BULLETS_TEXT = "Bullets"
HEALTH_TEXT = "Live"

BULLETS_EXPONENT = 1.4
"""Constants for generate bullets on map, with a greater distance from the start, their numbers are greatly reduced.

According to the following formula (distance is Euclidean distance from start):
p = min(BULLETS_MAX_PROB, (1/(distance^BULLETS_EXPONENT))*BULLETS_MULTIPLY)
Constants bellow can be change to manage difficulty.

The exponent specifies how quickly the difficulty will deteriorate.
The multiply constants do the linear scaling.
The max specifies the maximum on the start. Avoid all neighbors are bullets.
"""
BULLETS_MULTIPLY = 3
"""The mechanism of the effect of BULLETS_MULTIPLY on map generation is described in the BULLETS_EXPONENT comment."""
BULLETS_MAX_PROB = 0.05
"""The mechanism of the effect of BULLETS_MAX_PROB on map generation is described in the BULLETS_EXPONENT comment."""


HEALTH_EXPONENT = 1.4
"""Constants for generate healths on map, with a greater distance from the start, their numbers are greatly reduced.

According to the following formula (distance is Euclidean distance from start):
p = min(HEALTH_MAX_PROB, (1/(distance^HEALTH_EXPONENT))*HEALTH_MULTIPLY)
Constants bellow can be change to manage difficulty.

The exponent specifies how quickly the difficulty will deteriorate.
The multiply constants do the linear scaling.
The max specifies the maximum on the start. Avoid all neighbors are healths.
"""
HEALTH_MULTIPLY = 1
"""The mechanism of the effect of HEALTH_MULTIPLY on map generation is described in the HEALTH_EXPONENT comment."""
HEALTH_MAX_PROB = 0.01
"""The mechanism of the effect of HEALTH_MAX_PROB on map generation is described in the HEALTH_EXPONENT comment."""


ENEMY_START_PROBABILITY = 0.01
"""Constants for generate enemy on map, with a greater distance from the start, their number increases.

According to the following formula (distance is Euclidean distance from start):
p = min(ENEMY_MAX_PROB, ENEMY_START_PROBABILITY * (distance/ENEMY_DISTANCE_DIVIDER))
Constants bellow can be change to manage difficulty.

The distance divider uses to decrease the computed Euclidean distance from start to moderate difficulty increasing.
The start probability constants add the scale to the valnted value.
The max specifies the maximum. Avoid all fields are occupied by enemies.
"""
ENEMY_DISTANCE_DIVIDER = 10
"""The mechanism of the effect of ENEMY_DISTANCE_DIVIDER 
on map generation is described in the ENEMY_START_PROBABILITY comment."""
ENEMY_MAX_PROB = 0.05
"""The mechanism of the effect of ENEMY_MAX_PROB 
on map generation is described in the ENEMY_START_PROBABILITY comment."""


GUNS_EXPONENT = 1.4
"""Constants for generate guns on map, with a greater distance from the start, their numbers are greatly reduced.

According to the following formula (distance is Euclidean distance from start):
p = min(GUNS_MAX_PROB, (1/(distance^GUNS_EXPONENT))*GUNS_MULTIPLY)
Constants bellow can be change to manage difficulty.

The exponent specifies how quickly the difficulty will deteriorate.
The multiply constants do the linear scaling.
The max specifies the maximum on the start. Avoid all neighbors are guns.
"""
GUNS_MULTIPLY = 1
"""The mechanism of the effect of GUNS_MULTIPLY on map generation is described in the GUNS_EXPONENT comment."""
GUNS_MAX_PROB = 0.01
"""The mechanism of the effect of GUNS_MAX_PROB on map generation is described in the GUNS_EXPONENT comment."""
