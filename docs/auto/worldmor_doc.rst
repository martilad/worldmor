.. _worldmor:

WoldMor
==============================

Here is a description of the API interface of the WorldMor class with which work the gui part.
This class is write in Cython and have C constructor.
The values which are needed to be set are described below
and their usage in class is described in :ref:`game`.

WorldMor class C constructor parameters
------------------------------------------

- **rows** - start size of the map
- **random_seed** - seed for random generator, because C rand() is "hard" pseudo-random generator.
- **bullets_exponent, bullets_multiply, bullets_max_prob** - Describe in map generator section in :ref:`game`
- **health_exponent, health_multiply, health_max_prob** - Describe in map generator section in :ref:`game`
- **enemy_start_probability, enemy_distance_divider, enemy_max_prob** - Describe in map generator section in :ref:`game`
- **guns_exponent, guns_multiply, guns_max_prob** - Describe in map generator section in :ref:`game`
- **how_long_between_turn_ai** - Time moments between the enemy step or shoot.
- **go_for_player_ai_prob, go_for_gun_ai_prob, go_for_health_ai_prob, go_for_bullets_ai_prob** - Describe in enemies section in :ref:`game`
- **view_range** - View range of the player, how far the player sees the map and enemies and items.
- **check_range** - This not base on Euclidean distance, but the check area is :math:`4 \cdot \text{check_range}^2` with the player in the middle. In this area, the enemies do their steps.
- **how_far_see_ai** - The view range of the enemies

WorldMor class
---------------

.. automodule:: worldmor.game.game
    :members:
    :undoc-members:

WorldMor constants
-----------------------
.. automodule:: worldmor.constants
    :members:
    :undoc-members: