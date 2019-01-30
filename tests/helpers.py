from collections import OrderedDict
from worldmor.constants import *

data = OrderedDict(random_seed=10, bullets_exponent=BULLETS_EXPONENT,
                   bullets_multiply=BULLETS_MULTIPLY, bullets_max_prob=BULLETS_MAX_PROB,
                   health_exponent=HEALTH_EXPONENT, health_multiply=HEALTH_MULTIPLY,
                   health_max_prob=HEALTH_MAX_PROB, enemy_start_probability=ENEMY_START_PROBABILITY,
                   enemy_distance_divider=ENEMY_DISTANCE_DIVIDER, enemy_max_prob=ENEMY_MAX_PROB,
                   guns_exponent=GUNS_EXPONENT, guns_multiply=GUNS_MULTIPLY, guns_max_prob=GUNS_MAX_PROB,
                   how_far_see_ai=HOW_FAR_SEE_AI, how_long_between_turn_ai=HOW_LONG_BETWEEN_TURN_AI,
                   go_for_player_ai_prob=GO_FOR_PLAYER_AI_PROB, go_for_gun_ai_prob=GO_FOR_GUN_AI_PROB,
                   go_for_health_ai_prob=GO_FOR_HEALTH_AI_PROB, view_range=VIEW_RANGE,
                   go_for_bullets_ai_prob=GO_FOR_BULLETS_AI_PROB, check_range=CHECK_RANGE)
