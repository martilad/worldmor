from worldmor.game.game import *
from helpers import get_data
from worldmor.constants import *

EMPTY_MAP = np.zeros((5, 1), dtype=np.int64)


def test_init_set_and_get_params():
    """Test init the class and correctly set these values."""
    w = Worldmor(**get_data(), rows=10)
    assert w.get_pos_row() == 5
    assert w.get_pos_col() == 5
    assert w.get_mid_row() == 5
    assert w.get_mid_col() == 5
    assert w.get_ai_how_far_see() == HOW_FAR_SEE_AI
    assert w.get_how_fast_ai_is() == HOW_LONG_BETWEEN_TURN_AI
    w.set_pos_row(20)
    w.set_pos_col(21)
    w.set_mid_row(22)
    w.set_mid_col(23)
    w.set_ai_how_far_see(24)
    w.set_how_fast_ai_is(25)
    assert w.get_pos_row() == 20
    assert w.get_pos_col() == 21
    assert w.get_mid_row() == 22
    assert w.get_mid_col() == 23
    assert w.get_ai_how_far_see() == 24
    assert w.get_how_fast_ai_is() == 25


def test_move_left():
    w = Worldmor(**get_data(), rows=4)
    assert w.get_pos_row() == 2
    assert w.get_pos_col() == 2
    w.left()
    w.do_one_time_moment()
    assert w.get_pos_row() == 2
    assert w.get_pos_col() == 1


def test_move_down():
    w = Worldmor(**get_data(), rows=4)
    assert w.get_pos_row() == 2
    assert w.get_pos_col() == 2
    w.down()
    w.do_one_time_moment()
    assert w.get_pos_row() == 3
    assert w.get_pos_col() == 2


def test_move_up():
    w = Worldmor(**get_data(), rows=4)
    assert w.get_pos_row() == 2
    assert w.get_pos_col() == 2
    w.up()
    w.do_one_time_moment()
    assert w.get_pos_row() == 1
    assert w.get_pos_col() == 2


def test_move_right():
    w = Worldmor(**get_data(), rows=4)
    assert w.get_pos_row() == 2
    assert w.get_pos_col() == 2
    w.right()
    w.do_one_time_moment()
    assert w.get_pos_row() == 2
    assert w.get_pos_col() == 3


def test_worldmor_code_convertors():
    w = Worldmor(**get_data(), rows=4)
    code = 123456789876
    assert w.get_direction(code) == 3
    assert w.get_gun(code) == 12
    assert w.get_bullets(code) == 456
    assert w.get_health(code) == 789
    assert w.get_visible(code) == 8
    test = (76 + int(w.to_direction(3)) + w.to_gun(12) + int(w.to_bullets(456)) + w.to_health(789) + w.to_visible(8))
    assert code == test


def test_move_to_wall_position():
    """Test if wall block the move."""
    w = Worldmor(**get_data(), rows=4)
    EMPTY_MAP[2, 0] = PLAYER + w.to_direction(1) + w.to_gun(GUN_B) + w.to_bullets(100) + w.to_health(1)
    EMPTY_MAP[1, 0] = WALL
    w.set_pos_row(2)
    w.set_pos_col(0)
    w.set_mid_row(2)
    w.set_mid_col(0)
    w.put_map_to_game(EMPTY_MAP)
    w.up()
    w.do_one_time_moment()
    assert w.get_pos_row() == 2
    assert w.get_pos_col() == 0


def test_destroy_wall_position():
    """Test shoot after shoot before move to position of wall and test move to wall before shoot in one time moment"""
    w = Worldmor(**get_data(), rows=4)
    # add player direction, health, gun and bullets
    EMPTY_MAP[2, 0] = PLAYER + w.to_direction(1) + w.to_gun(GUN_B) + w.to_bullets(100) + w.to_health(1)
    EMPTY_MAP[1, 0] = WALL + w.to_health(1)
    EMPTY_MAP[0, 0] = WALL + w.to_health(1)
    w.set_pos_row(2)
    w.set_pos_col(0)
    w.set_mid_row(2)
    w.set_mid_col(0)
    w.put_map_to_game(EMPTY_MAP)
    # destroy wall and move
    w.shoot()
    w.up()
    assert w.do_one_time_moment() == 0
    assert w.get_pos_row() == 1
    assert w.get_pos_col() == 0
    # move cant and then destroy wall
    w.up()
    w.shoot()
    assert w.do_one_time_moment() == 0
    assert w.get_pos_row() == 1
    assert w.get_pos_col() == 0
    # Try if the wall wal destroyed, move there
    w.up()
    assert w.do_one_time_moment() == 0
    assert w.get_pos_row() == 0
    assert w.get_pos_col() == 0


def test_move_and_pickup_for_bullets():
    w = Worldmor(**get_data(), rows=4)
    # add player direction, health, gun and bullets
    set_code = PLAYER + w.to_gun(GUN_B) + w.to_bullets(1) + w.to_health(1)
    EMPTY_MAP[2, 0] = set_code
    EMPTY_MAP[1, 0] = BULLET
    w.set_pos_row(2)
    w.set_pos_col(0)
    w.set_mid_row(2)
    w.set_mid_col(0)
    w.put_map_to_game(EMPTY_MAP)
    code = w.get_map_to_save()[2, 0]
    assert code == set_code
    w.up()
    assert w.do_one_time_moment() == 0
    code = w.get_map_to_save()[1, 0]
    # add some bullets, and no other code change
    assert w.get_bullets(code) > 1
    assert w.get_health(code) == 1
    assert w.get_gun(code) == GUN_B
    assert code % 100 == PLAYER
    # check pick up and move
    assert w.get_pos_row() == 1
    assert w.get_pos_col() == 0
    # Test field of position before are grass with visibility 1
    assert w.get_map_to_save()[2, 0] == 100


def test_move_and_pickup_for_health():
    w = Worldmor(**get_data(), rows=4)
    # add player direction, health, gun and bullets
    set_code = PLAYER + w.to_gun(GUN_B) + w.to_bullets(1) + w.to_health(1)
    EMPTY_MAP[2, 0] = set_code
    EMPTY_MAP[1, 0] = HEALTH
    w.set_pos_row(2)
    w.set_pos_col(0)
    w.set_mid_row(2)
    w.set_mid_col(0)
    w.put_map_to_game(EMPTY_MAP)
    code = w.get_map_to_save()[2, 0]
    assert code == set_code
    w.up()
    assert w.do_one_time_moment() == 0
    code = w.get_map_to_save()[1, 0]
    # add some bullets, and no other code change
    assert w.get_bullets(code) == 1
    assert w.get_health(code) > 1
    assert w.get_gun(code) == GUN_B
    assert code % 100 == PLAYER
    # check pick up and move
    assert w.get_pos_row() == 1
    assert w.get_pos_col() == 0
    # Test field of position before are grass with visibility 1
    assert w.get_map_to_save()[2, 0] == 100


def test_move_and_pickup_for_gun():
    w = Worldmor(**get_data(), rows=4)
    # add player direction, health, gun and bullets
    set_code = PLAYER + w.to_gun(GUN_B) + w.to_bullets(1) + w.to_health(1)
    EMPTY_MAP[2, 0] = set_code
    EMPTY_MAP[1, 0] = GUN_3
    w.set_pos_row(2)
    w.set_pos_col(0)
    w.set_mid_row(2)
    w.set_mid_col(0)
    w.put_map_to_game(EMPTY_MAP)
    code = w.get_map_to_save()[2, 0]
    assert code == set_code
    w.up()
    assert w.do_one_time_moment() == 0
    code = w.get_map_to_save()[1, 0]
    # add some bullets, and no other code change
    assert w.get_bullets(code) == 1
    assert w.get_health(code) == 1
    assert w.get_gun(code) == GUN_3
    assert code % 100 == PLAYER
    # check pick up and move
    assert w.get_pos_row() == 1
    assert w.get_pos_col() == 0
    # Test field of position before are grass with visibility 1
    assert w.get_map_to_save()[2, 0] == 100


def test_killing_enemy():
    """Test if I can kill enemy and catch the points."""
    w = Worldmor(**get_data(), rows=4)
    # add player direction, health, gun and bullets
    set_code = PLAYER + w.to_direction(1) + w.to_gun(GUN_E) + w.to_bullets(100) + w.to_health(1)
    EMPTY_MAP[2, 0] = set_code
    EMPTY_MAP[1, 0] = ENEMY_B + w.to_health(1)
    w.set_pos_row(2)
    w.set_pos_col(0)
    w.set_mid_row(2)
    w.set_mid_col(0)
    w.put_map_to_game(EMPTY_MAP)
    code = w.get_map_to_save()[2, 0]
    assert code == set_code
    # Kill the enemy
    w.shoot()
    assert w.do_one_time_moment() == 0
    code = w.get_map_to_save()[1, 0]
    # blood after kill, it must be visible?
    assert code == BLOOD + w.to_visible(1)
    # collect the points
    w.up()
    assert w.do_one_time_moment() > 0
    # check pick up and move
    assert w.get_pos_row() == 1
    assert w.get_pos_col() == 0
    # Test field of position before are grass with visibility 1
    assert w.get_map_to_save()[2, 0] == 100
