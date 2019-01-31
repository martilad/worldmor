from worldmor.game.game import *
from helpers import get_data


EMPTY_MAP = np.zeros((11, 11), dtype=np.int64)


def test_check_range():
    """Check if only move the enemies in the check range."""

    data = get_data()
    # when ai in check range he see me
    data['check_range'] = 4
    data['how_far_see_ai'] = 10
    w = Worldmor(**data, rows=11)
    EMPTY_MAP[5, 5] = PLAYER + w.to_direction(1) + w.to_gun(GUN_B) + w.to_bullets(100) + w.to_health(1)
    # enemy in of range of check - move near to me
    EMPTY_MAP[1, 5] = ENEMY_B + w.to_health(1)
    # enemy out of range of check - not move
    EMPTY_MAP[10, 5] = ENEMY_B + w.to_health(1)

    w.put_map_to_game(EMPTY_MAP)
    w.set_pos_row(5)
    w.set_pos_col(5)
    w.set_mid_row(5)
    w.set_mid_col(5)
    w.do_one_time_moment()

    # check the map
    assert w.get_map_to_save()[10, 5] % 100 == ENEMY_B
    assert w.get_map_to_save()[1, 5] % 100 == GRASS
    assert w.get_map_to_save()[2, 5] % 100 == ENEMY_B
    assert w.get_map_to_save()[5, 5] % 100 == PLAYER


def test_shoot_when_can():
    """Check if enemy shoot if they can shoot."""

    data = get_data()
    # when ai in check range he see me
    data['check_range'] = 4
    data['how_far_see_ai'] = 10
    w = Worldmor(**data, rows=11)
    EMPTY_MAP[5, 5] = PLAYER + w.to_direction(1) + w.to_gun(GUN_B) + w.to_bullets(100) + w.to_health(1)
    # enemy out of range of check range not move, have big gun with a maximum set shoot range
    EMPTY_MAP[10, 5] = ENEMY_B + w.to_health(1) + w.to_gun(GUN_E) + w.to_bullets(100)

    w.put_map_to_game(EMPTY_MAP)
    w.set_pos_row(5)
    w.set_pos_col(5)
    w.set_mid_row(5)
    w.set_mid_col(5)
    w.do_one_time_moment()

    # not change enemy not in move range
    assert w.get_map_to_save()[10, 5] % 100 == ENEMY_B
    assert w.get_map_to_save()[5, 5] % 100 == PLAYER

    # move near to the check range
    w.down()
    # enemy can shoot and shoot to me and kill me (1 health) so check return value and map after game time moment.
    assert w.do_one_time_moment() == -1
    # not change enemy not in move range
    assert w.get_map_to_save()[10, 5] % 100 == ENEMY_B
    assert w.get_map_to_save()[6, 5] % 100 == BLOOD


def test_ai_view_range():
    """Check if only move the enemies in the check range."""

    EMPTY_MAP = np.zeros((11, 11), dtype=np.int64)

    data = get_data()
    # when ai in check range he see me
    data['check_range'] = 6
    data['how_far_see_ai'] = 3
    w = Worldmor(**data, rows=11)
    EMPTY_MAP[5, 5] = PLAYER + w.to_direction(1) + w.to_gun(GUN_B) + w.to_bullets(100) + w.to_health(1)
    # enemy which can see me, should move to me
    EMPTY_MAP[5, 2] = ENEMY_B + w.to_health(1) + w.to_bullets(100) + w.to_gun(GUN_B)
    # Not see me can do random walk
    EMPTY_MAP[5, 9] = ENEMY_B + w.to_health(1) + w.to_bullets(100) + w.to_gun(GUN_B)

    w.put_map_to_game(EMPTY_MAP)
    w.set_pos_row(5)
    w.set_pos_col(5)
    w.set_mid_row(5)
    w.set_mid_col(5)
    w.do_one_time_moment()

    # check the map
    assert (w.get_map_to_save()[5, 10] % 100 == ENEMY_B or w.get_map_to_save()[5, 8] % 100 == ENEMY_B or
            w.get_map_to_save()[4, 9] % 100 == ENEMY_B or w.get_map_to_save()[6, 9] % 100 == ENEMY_B or
            w.get_map_to_save()[5, 9] % 100 == ENEMY_B)
    assert w.get_map_to_save()[5, 2] % 100 == GRASS
    assert w.get_map_to_save()[5, 3] % 100 == ENEMY_B
    assert w.get_map_to_save()[5, 5] % 100 == PLAYER


def test_ai_fast():
    """Test ai steps wait. Test fail possible if the range of GUN_B change."""

    EMPTY_MAP = np.zeros((11, 11), dtype=np.int64)

    data = get_data()

    w = Worldmor(**data, rows=11)
    EMPTY_MAP[5, 5] = PLAYER + w.to_direction(1) + w.to_gun(GUN_B) + w.to_bullets(100) + w.to_health(1)

    # Not see me can do random walk
    EMPTY_MAP[5, 9] = ENEMY_B + w.to_health(1) + w.to_bullets(100) + w.to_gun(GUN_B)

    w.put_map_to_game(EMPTY_MAP)
    w.set_pos_row(5)
    w.set_pos_col(5)
    w.set_mid_row(5)
    w.set_mid_col(5)
    # wait 5 time moments
    w.set_how_fast_ai_is(5)
    # need se to see me for deterministic walk or shoot
    w.set_ai_how_far_see(10)
    # so move near to me
    w.do_one_time_moment()

    assert w.get_map_to_save()[5, 8] % 100 == ENEMY_B
    assert w.get_direction(w.get_map_to_save()[5, 8]) == 5
    assert w.get_map_to_save()[5, 5] % 100 == PLAYER

    for i in range(5):
        w.do_one_time_moment()

    assert w.get_map_to_save()[5, 8] % 100 == ENEMY_B
    assert w.get_direction(w.get_map_to_save()[5, 8]) == 0
    assert w.get_map_to_save()[5, 5] % 100 == PLAYER

    w.do_one_time_moment()
    assert w.get_map_to_save()[5, 7] % 100 == ENEMY_B
    assert w.get_direction(w.get_map_to_save()[5, 8]) == 0

    for i in range(5):
        w.do_one_time_moment()

    assert w.do_one_time_moment() == -1
    assert w.get_map_to_save()[5, 5] % 100 == BLOOD


def test_go_for_player_ai():
    """Test if ai go for player right if the probability is 100%."""

    EMPTY_MAP = np.zeros((11, 11), dtype=np.int64)
    data = get_data()
    data['go_for_player_ai_prob'] = 1
    data['go_for_gun_ai_prob'] = 0
    data['go_for_health_ai_prob'] = 0
    data['go_for_bullets_ai_prob'] = 0
    # not see but can move to player, this have some not 0 probability
    data['how_far_see_ai'] = 0
    w = Worldmor(**data, rows=11)
    EMPTY_MAP[4, 4] = PLAYER + w.to_direction(1) + w.to_gun(GUN_B) + w.to_bullets(100) + w.to_health(1)
    # test enemy to move nearest gun in see
    EMPTY_MAP[4, 10] = ENEMY_B + w.to_health(1) + w.to_gun(GUN_B) + w.to_bullets(100)

    w.put_map_to_game(EMPTY_MAP)
    w.set_pos_row(4)
    w.set_pos_col(4)
    w.set_mid_row(5)
    w.set_mid_col(5)
    w.set_how_fast_ai_is(0)  # dont want to wait
    w.do_one_time_moment()

    # Enemy have the gun new?
    assert w.get_map_to_save()[4, 10] % 100 == GRASS
    assert w.get_map_to_save()[4, 9] % 100 == ENEMY_B


def test_go_for_gun():
    """Test if ai go for gun right if the probability is 100%."""

    EMPTY_MAP = np.zeros((11, 11), dtype=np.int64)
    data = get_data()
    data['go_for_player_ai_prob'] = 0
    data['go_for_gun_ai_prob'] = 1
    data['go_for_health_ai_prob'] = 0
    data['go_for_bullets_ai_prob'] = 0
    data['how_far_see_ai'] = 4
    w = Worldmor(**data, rows=11)
    EMPTY_MAP[4, 4] = PLAYER + w.to_direction(1) + w.to_gun(GUN_B) + w.to_bullets(100) + w.to_health(1)
    # test enemy to move nearest gun in see
    EMPTY_MAP[10, 10] = ENEMY_B + w.to_health(1) + w.to_gun(GUN_B) + w.to_bullets(100)
    EMPTY_MAP[8, 10] = GUN_E
    EMPTY_MAP[8, 7] = GUN_E

    w.put_map_to_game(EMPTY_MAP)
    w.set_pos_row(4)
    w.set_pos_col(4)
    w.set_mid_row(5)
    w.set_mid_col(5)
    w.set_how_fast_ai_is(0) # dont want to wait
    w.do_one_time_moment()

    # Enemy have the gun new?
    assert w.get_map_to_save()[10, 10] % 100 == GRASS
    assert w.get_map_to_save()[9, 10] % 100 == ENEMY_B
    assert w.get_gun(w.get_map_to_save()[9, 10]) == GUN_B

    # Take the gun
    w.do_one_time_moment()
    assert w.get_map_to_save()[9, 10] % 100 == GRASS
    assert w.get_map_to_save()[8, 10] % 100 == ENEMY_B
    assert w.get_gun(w.get_map_to_save()[8, 10]) == GUN_E


def test_go_for_bullets():
    """Test if ai go for bullets right if the probability is 100% or more."""

    EMPTY_MAP = np.zeros((11, 11), dtype=np.int64)
    data = get_data()
    data['go_for_player_ai_prob'] = 0
    data['go_for_gun_ai_prob'] = 0
    data['go_for_health_ai_prob'] = 0
    data['go_for_bullets_ai_prob'] = 1
    data['how_far_see_ai'] = 4
    w = Worldmor(**data, rows=11)
    EMPTY_MAP[4, 4] = PLAYER + w.to_direction(1) + w.to_gun(GUN_B) + w.to_bullets(100) + w.to_health(1)
    # test enemy to move nearest bullets in see
    EMPTY_MAP[10, 10] = ENEMY_B + w.to_health(1) + w.to_gun(GUN_B) + w.to_bullets(0)
    EMPTY_MAP[8, 10] = BULLET
    EMPTY_MAP[8, 7] = BULLET

    w.put_map_to_game(EMPTY_MAP)
    w.set_pos_row(4)
    w.set_pos_col(4)
    w.set_mid_row(5)
    w.set_mid_col(5)
    w.set_how_fast_ai_is(0)  # dont want to wait
    w.do_one_time_moment()

    # Enemy have the gun new?
    assert w.get_map_to_save()[10, 10] % 100 == GRASS
    assert w.get_map_to_save()[9, 10] % 100 == ENEMY_B
    assert w.get_bullets(w.get_map_to_save()[9, 10]) == 0

    # Take the gun
    w.do_one_time_moment()
    assert w.get_map_to_save()[9, 10] % 100 == GRASS
    assert w.get_map_to_save()[8, 10] % 100 == ENEMY_B
    # get some bullets
    assert w.get_bullets(w.get_map_to_save()[8, 10]) > 0


def test_go_for_bullets_when_not_have():
    """Test enemy go for bullets after shoot last bullets to player and then continue shooting.
    Test can fail if the damage of the base gun change.
    """

    EMPTY_MAP = np.zeros((11, 11), dtype=np.int64)
    data = get_data()
    data['go_for_player_ai_prob'] = 0
    data['go_for_gun_ai_prob'] = 0
    data['go_for_health_ai_prob'] = 0
    data['go_for_bullets_ai_prob'] = 1
    data['how_far_see_ai'] = 8
    w = Worldmor(**data, rows=11)
    # Dont die for first shoot but second can
    EMPTY_MAP[5, 4] = PLAYER + w.to_direction(1) + w.to_gun(GUN_B) + w.to_bullets(100) + w.to_health(12)
    # test enemy to move nearest bullets in see
    EMPTY_MAP[5, 6] = ENEMY_B + w.to_health(1) + w.to_gun(GUN_B) + w.to_bullets(1)
    EMPTY_MAP[5, 9] = BULLET

    w.put_map_to_game(EMPTY_MAP)
    w.set_pos_row(5)
    w.set_pos_col(4)
    w.set_mid_row(5)
    w.set_mid_col(4)
    w.set_how_fast_ai_is(1)  # dont want to wait
    # should shoot to me
    w.do_one_time_moment()
    assert w.get_map_to_save()[5, 4] % 100 == PLAYER
    assert w.get_health(w.get_map_to_save()[5, 4]) < 12

    assert w.get_map_to_save()[5, 6] % 100 == ENEMY_B
    assert w.get_bullets(w.get_map_to_save()[5, 6]) == 0

    # no bullets let go for some
    w.do_one_time_moment()
    w.do_one_time_moment()
    assert w.get_map_to_save()[5, 7] % 100 == ENEMY_B
    w.do_one_time_moment()
    assert w.get_map_to_save()[5, 8] % 100 == ENEMY_B
    w.do_one_time_moment()
    assert w.get_map_to_save()[5, 9] % 100 == ENEMY_B
    assert w.get_bullets(w.get_map_to_save()[5, 9]) > 0

    # Lets go back and kill the player
    w.do_one_time_moment()
    w.do_one_time_moment()
    assert w.get_map_to_save()[5, 8] % 100 == ENEMY_B
    w.do_one_time_moment()
    w.do_one_time_moment()
    assert w.get_map_to_save()[5, 7] % 100 == ENEMY_B
    w.do_one_time_moment()
    w.do_one_time_moment()
    assert w.get_map_to_save()[5, 6] % 100 == ENEMY_B
    w.do_one_time_moment()
    w.do_one_time_moment()
    assert w.get_map_to_save()[5, 4] % 100 == BLOOD


def test_go_for_health():
    """Test if ai go for health right if the probability is 100% or more."""

    EMPTY_MAP = np.zeros((11, 11), dtype=np.int64)
    data = get_data()
    data['go_for_player_ai_prob'] = 0
    data['go_for_gun_ai_prob'] = 0
    # It is not good have probability larger than 100% (from formulas describe in documentation) only good for test.
    data['go_for_health_ai_prob'] = 1.5
    data['go_for_bullets_ai_prob'] = 0
    data['how_far_see_ai'] = 4
    w = Worldmor(**data, rows=11)
    EMPTY_MAP[4, 4] = PLAYER + w.to_direction(1) + w.to_gun(GUN_B) + w.to_bullets(100) + w.to_health(1)
    # test enemy to move nearest gun in see
    EMPTY_MAP[10, 10] = ENEMY_B + w.to_health(1) + w.to_gun(GUN_B) + w.to_bullets(100)
    EMPTY_MAP[8, 10] = HEALTH
    EMPTY_MAP[8, 7] = HEALTH

    w.put_map_to_game(EMPTY_MAP)
    w.set_pos_row(4)
    w.set_pos_col(4)
    w.set_mid_row(5)
    w.set_mid_col(5)
    w.set_how_fast_ai_is(0)  # dont want to wait
    w.do_one_time_moment()

    # Enemy have the gun new?
    assert w.get_map_to_save()[10, 10] % 100 == GRASS
    assert w.get_map_to_save()[9, 10] % 100 == ENEMY_B
    assert w.get_health(w.get_map_to_save()[9, 10]) == 1

    # Take the gun
    w.do_one_time_moment()
    assert w.get_map_to_save()[9, 10] % 100 == GRASS
    assert w.get_map_to_save()[8, 10] % 100 == ENEMY_B
    # enemy get some health from pharmacy
    assert w.get_health(w.get_map_to_save()[8, 10]) > 1
