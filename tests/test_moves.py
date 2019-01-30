import pytest
from worldmor.game.game import Worldmor
from helpers import data
from worldmor.constants import *


def test_init_set_and_get_params():
    """Test init the class and correctly set these values."""
    w = Worldmor(**data, rows=10)
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
    w = Worldmor(**data, rows=4)
    assert w.get_pos_row() == 2
    assert w.get_pos_col() == 2
    w.left()
    w.do_one_time_moment()
    assert w.get_pos_row() == 2
    assert w.get_pos_col() == 1


def test_move_down():
    w = Worldmor(**data, rows=4)
    assert w.get_pos_row() == 2
    assert w.get_pos_col() == 2
    w.down()
    w.do_one_time_moment()
    assert w.get_pos_row() == 3
    assert w.get_pos_col() == 2

def test_move_up():
    w = Worldmor(**data, rows=4)
    assert w.get_pos_row() == 2
    assert w.get_pos_col() == 2
    w.up()
    w.do_one_time_moment()
    assert w.get_pos_row() == 1
    assert w.get_pos_col() == 2


def test_move_right():
    w = Worldmor(**data, rows=4)
    assert w.get_pos_row() == 2
    assert w.get_pos_col() == 2
    w.right()
    w.do_one_time_moment()
    assert w.get_pos_row() == 2
    assert w.get_pos_col() == 3





