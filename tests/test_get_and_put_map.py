from worldmor.game.game import *
from helpers import get_data
from worldmor.constants import *


def test_load_and_save_game():
    """Test saving the game. Init empty game with player with some walls -> save game -> do some steps ->
    -> then load save state and try other steps."""
    data = get_data()
    # test map generator for large map
    data['rows'] = 50
    w = Worldmor(**data)
    player = PLAYER + w.to_direction(1) + w.to_gun(GUN_B) + w.to_bullets(100) + w.to_health(1)
    # Init the game with one player between walls
    EMPTY_MAP = np.zeros((20, 20), dtype=np.int64)
    EMPTY_MAP[10, 10] = PLAYER + w.to_direction(1) + w.to_gun(GUN_B) + w.to_bullets(100) + w.to_health(1)
    EMPTY_MAP[9, 10] = WALL + w.to_health(1)
    EMPTY_MAP[10, 9] = WALL + w.to_health(1)
    EMPTY_MAP[11, 10] = WALL + w.to_health(1)
    EMPTY_MAP[10, 11] = WALL + w.to_health(1)
    w.set_pos_row(10)
    w.set_pos_col(10)
    w.set_mid_row(10)
    w.set_mid_col(10)
    w.put_map_to_game(EMPTY_MAP)

    # save the game
    save_map = w.get_map_to_save()
    save_posr = w.get_pos_row()
    save_posc = w.get_pos_col()
    save_midr = w.get_mid_row()
    save_midc = w.get_mid_col()
    save_aisee = w.get_ai_how_far_see()
    save_aifast = w.get_how_fast_ai_is()

    # set level ai to 3
    w.set_how_fast_ai_is(LEVEL_3_AI_FAST)
    w.set_ai_how_far_see(LEVEL_3_AI_SIGHT)

    # shoot the wall
    w.shoot()
    w.do_one_time_moment()
    # move
    w.up()
    w.do_one_time_moment()

    # check move must be successful, steps are done
    check = w.get_map_to_save()
    assert check[10, 10] == GRASS + w.to_visible(1)

    # do load game procedure
    w.put_map_to_game(save_map)
    w.set_ai_how_far_see(save_aisee)
    w.set_how_fast_ai_is(save_aifast)
    w.set_pos_row(save_posr)
    w.set_mid_col(save_midc)
    w.set_mid_row(save_midr)
    w.set_pos_col(save_posc)

    w.down()
    w.shoot()
    w.do_one_time_moment()
    w.down()
    w.do_one_time_moment()

    # In up position is wall, modle grass and down is the player witch 0 bullets
    check = w.get_map_to_save()

    # Test status from save state
    assert check[10, 10] == int(GRASS + w.to_visible(1))
    assert check[9, 10] == int(WALL + w.to_visible(1) + w.to_health(1))
    assert check[11, 10] == int(PLAYER + w.to_visible(1) + w.to_health(1) +
                                w.to_direction(3) + w.to_gun(GUN_B) + w.to_bullets(99))
