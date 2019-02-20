=========
WorldMor
=========

|license| |doc| |travis| |pypi|


**WorldMor** is an application (game) write in Python using framework PyQt.
It is created as a semestral work of **MI-PYT** course at **CTU in Prague**.

In this game, it's an effort to get the best score on the map in the selected level.
The map contains the crafts, bullets, weapons, and of course enemies, which is the task of destroying.
The Enemies can also collect these items.
With time when the distance from the start is more significant the count of objects on the map decreasing,
and the number of enemies increasing. The game can also be played in fullscreen mode.
There are three levels of difficulty that are specified by enemy surveillance and their speed.

Installation
-------------

- Game is released on `Pypi`_.
- This game can be install using pip.
- Use following command: ``python -m pip install worldmor``

Control and aim of the game
-----------------------------

You can use WSAD or arrows to walk, and you can use Spacebar or 0 to shoot.
The body always shoots in the direction of movement.

The goal of the game is to destroy the enemy,
after each destroyed extra-emblem, there is blood on the map that points,
but the attention need not be collected by you alone.
The game ends after you've been killed.
The number of objects on the map drops to a minimum and the number of
enemies increases with the distance from start, which will soon bring about an end.

Semestral work assignment
----------------------------

The work aims to create a game that will take place on a 2D endless map.
Your aim of the game will be to get the highest score.

The map itself is endless. Visibility is limited.
The map finds aliens (opponents) controlled by some artificial intelligence (more likely to settle the difficulty).
Their goal is your destruction of course, but they have more primitive weapons than you can find.

The score can be obtained for the destruction of computer opponents.
Some bonuses can also be placed on the map, where you can get points and
weapons which can help you destroy computer opponents.

Weapons will have a different range of damage which they can cause.
Also, weapons will have a range. With the use of weapons, it is clear
that everyone on the map will have his own life. This can be supplemented by some pharmacies.

With increasing time, the game will become more and more difficult,
the number of opponents will increase, and the number of weapons, pharmacies on the map will decreasing.

Specifications:

- Fullscreen mode
- The ability to save and load a saved game
- Increasing skill on an endless map
- Several levels of enemy intelligence
- Some different types of weapons


Build from repository
-----------------------

For editing and local use, it is also possible to download this repository and to bring the game directly from it.
Try following commands:

1. Clone **WorldMor** from `repository`_.
2. Go into the cloned directory.
3. Run ``python -m pip install -r requirements.txt``
4. Use the following command to build Cython code for your system: ``python setup.py develop``
5. Now you can run game using ``python -m worldmor``


Documentation
--------------

The documentation are build using `ReadTheDocs`_
and you can find it at `WorldMorDoc`_

Also the documentation can build using the following steps:

1. Clone **WorldMor** from `repository`_.
2. Go into the cloned directory.
3. Run ``python -m pip install -r requirements.txt``
4. Use the following command to build Cython code for your system: ``python setup.py develop``
5. Go to **docs** directory inside the **WorldMor**.
6. Run ``make html``
7. You can find all of the .html files in _build/html directory


License
-------------

This project is licensed under the **GNU GPLv3**.

.. _repository: https://github.com/martilad/worldmor
.. _Pypi: https://pypi.org/project/worldmor/
.. _WorldMorDoc: https://worldmor.readthedocs.io/en/latest/?badge=latest
.. _ReadTheDocs: https://readthedocs.org/


.. |license| image:: https://img.shields.io/badge/license-GPLv3-blue.svg
    :alt: License
    :target: LICENSE


.. |doc| image:: https://readthedocs.org/projects/worldmor/badge/?version=latest
    :alt: Documentation Status
    :target: https://worldmor.readthedocs.io/en/latest/?badge=latest


.. |travis| image:: https://travis-ci.com/martilad/worldmor.svg?branch=master
    :alt: PyPi Version
    :target: https://travis-ci.com/martilad/worldmor

.. |pypi| image:: https://badge.fury.io/py/worldmor.svg
    :alt: Build Status
    :target: https://badge.fury.io/py/worldmor
