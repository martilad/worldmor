from worldmor.game.game import *
from helpers import get_data
import pytest

TEST_SIZE = 300


def test_generate_empty_map_with_walls():
    """Set all probabilities to 0 for items and test if there are only grass or walls."""
    data = get_data()
    # test map generator for large map
    data['rows'] = TEST_SIZE
    data['enemy_max_prob'] = 0
    data['health_max_prob'] = 0
    data['guns_max_prob'] = 0
    data['bullets_max_prob'] = 0
    data['view_range'] = 0
    w = Worldmor(**data)
    wall_check = WALL + w.to_health(100)
    for er, i in enumerate(w.get_map_to_save()):
        for ec, j in enumerate(i):
            if er == w.get_pos_row() and ec == w.get_pos_col():
                continue
            else:
                # there can be walls(generator logic are inside) or blood (some bonus with very small probability)
                # But there are no pharmacies, bullets, enemies and guns
                assert (j == GRASS or j == wall_check or j == 2)


@pytest.mark.parametrize('params', (('bullets_max_prob', 'bullets_exponent', "bullets_multiply", BULLET, BULLET),
                                    ('health_max_prob', 'health_exponent', "health_multiply", HEALTH, HEALTH),
                                    ('guns_max_prob', 'guns_exponent', "guns_multiply", GUN_B, GUN_E)))
def test_generate_map_only_with_items(params):
    """Set probability of items in parametrize to 1 test there are only the items and
    wall or blood for distance which is far as view range.
    In view range is protection zone.
    """
    data = get_data()
    # test map generator for large map
    data['rows'] = TEST_SIZE
    data['health_max_prob'] = 0
    data['guns_max_prob'] = 0
    data['enemy_max_prob'] = 0
    data['bullets_max_prob'] = 0
    # this do bullets probability to 1
    data[params[0]] = 1
    data[params[1]] = 0
    data[params[2]] = 1
    data['view_range'] = 0
    w = Worldmor(**data)
    wall_check = WALL + w.to_health(100)
    print(w.get_map_to_save())
    for er, i in enumerate(w.get_map_to_save()):
        for ec, j in enumerate(i):
            if er == w.get_pos_row() and ec == w.get_pos_col():
                continue
            else:
                # there can be walls(generator logic are inside) or blood (some bonus with very small probability)
                # But there are no pharmacies, bullets, enemies and guns
                assert (j == wall_check or params[3] <= j % 100 <= params[4] or j == 2)


def test_generate_map_only_with_enemies():
    """Set probability of enemies to 1 test there are only bullets and
    wall for distance which is far as view range.
    In view range is protection zone.
    """
    data = get_data()
    # test map generator for large map
    data['rows'] = TEST_SIZE
    data['enemy_max_prob'] = 1
    data['health_max_prob'] = 0
    data['guns_max_prob'] = 0
    data['bullets_max_prob'] = 0
    # this do bullets probability to 1
    data['enemy_max_prob'] = 1
    data['enemy_distance_divider'] = 1
    data['enemy_start_probability'] = 1
    data['view_range'] = 0
    w = Worldmor(**data)
    wall_check = WALL + w.to_health(100)
    print(w.get_map_to_save())
    for er, i in enumerate(w.get_map_to_save()):
        for ec, j in enumerate(i):
            if er == w.get_pos_row() and ec == w.get_pos_col():
                continue
            else:
                # there can be walls(generator logic are inside) or blood (some bonus with very small probability)
                # But there are no pharmacies, bullets, enemies and guns
                assert (j == wall_check or ENEMY_B <= j % 100 <= ENEMY_E or j == 2)
