from worldmor.game.game import *
from helpers import get_data

EMPTY_MAP = np.zeros((5, 5), dtype=np.int64)


def test_generate_new_part_of_map_left():
    """Test if map refactor left when use it. Cant be set the map values because it is generate randomly."""
    w = Worldmor(**get_data(), rows=10)
    EMPTY_MAP[2, 2] = PLAYER + w.to_direction(1) + w.to_gun(GUN_B) + w.to_bullets(100) + w.to_health(1)
    w.put_map_to_game(EMPTY_MAP)
    w.set_pos_row(2)
    w.set_pos_col(2)
    w.set_mid_row(2)
    w.set_mid_col(2)
    w.left()
    w.do_one_time_moment()
    w.left()
    w.do_one_time_moment()
    w.get_map(3, 3)
    assert w.get_map_to_save().shape == (5, 10)
    assert w.get_pos_row() == 2
    assert w.get_pos_col() == 5
    assert w.get_mid_row() == 2
    assert w.get_mid_col() == 7


def test_generate_new_part_of_map_up():
    """Test if map refactor up when use it. Cant be set the map values because it is generate randomly."""
    w = Worldmor(**get_data(), rows=10)
    EMPTY_MAP[2, 2] = PLAYER + w.to_direction(1) + w.to_gun(GUN_B) + w.to_bullets(100) + w.to_health(1)
    w.put_map_to_game(EMPTY_MAP)
    w.set_pos_row(2)
    w.set_pos_col(2)
    w.set_mid_row(2)
    w.set_mid_col(2)
    w.up()
    w.do_one_time_moment()
    w.up()
    w.do_one_time_moment()
    w.get_map(3, 3)
    assert w.get_map_to_save().shape == (10, 5)
    assert w.get_pos_row() == 5
    assert w.get_pos_col() == 2
    assert w.get_mid_row() == 7
    assert w.get_mid_col() == 2


def test_generate_new_part_of_map_right():
    """Test if map refactor right when use it. Cant be set the map values because it is generate randomly."""
    w = Worldmor(**get_data(), rows=10)
    EMPTY_MAP[2, 2] = PLAYER + w.to_direction(1) + w.to_gun(GUN_B) + w.to_bullets(100) + w.to_health(1)
    w.put_map_to_game(EMPTY_MAP)
    w.set_pos_row(2)
    w.set_pos_col(2)
    w.set_mid_row(2)
    w.set_mid_col(2)
    w.right()
    w.do_one_time_moment()
    w.right()
    w.do_one_time_moment()
    w.get_map(3, 3)
    assert w.get_map_to_save().shape == (5, 10)
    assert w.get_pos_row() == 2
    assert w.get_pos_col() == 4
    assert w.get_mid_row() == 2
    assert w.get_mid_col() == 2


def test_generate_new_part_of_map_down():
    """Test if map refactor down when use it. Cant be set the map values because it is generate randomly."""
    w = Worldmor(**get_data(), rows=10)
    EMPTY_MAP[2, 2] = PLAYER + w.to_direction(1) + w.to_gun(GUN_B) + w.to_bullets(100) + w.to_health(1)
    w.put_map_to_game(EMPTY_MAP)
    w.set_pos_row(2)
    w.set_pos_col(2)
    w.set_mid_row(2)
    w.set_mid_col(2)
    w.down()
    w.do_one_time_moment()
    w.down()
    w.do_one_time_moment()
    w.get_map(3, 3)
    assert w.get_map_to_save().shape == (10, 5)
    assert w.get_pos_row() == 4
    assert w.get_pos_col() == 2
    assert w.get_mid_row() == 2
    assert w.get_mid_col() == 2
