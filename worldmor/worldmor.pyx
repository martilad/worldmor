#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
import numpy as np

cimport numpy as np
cimport cython

from cpython.mem cimport PyMem_Malloc, PyMem_Free
from libc.stdlib cimport rand, srand, RAND_MAX
from libc.math cimport sqrt

"""Enum for items, players and environments of the map."""
cpdef enum:
    GRASS = 0
    WALL = 1
    BLOOD = 2
    PLAYER = 3
    BULLET = 4
    HEALTH = 5

    ENEMY_B = 6
    ENEMY_1 = 7
    ENEMY_2 = 8
    ENEMY_E = 9

    GUN_B = 12
    GUN_1 = 13
    GUN_2 = 14
    GUN_3 = 15
    GUN_E = 16

    EXPLODE = 21

"""Start zone where are no items generated."""
cdef int STARTING_PROTECTION_ZONE = 4
"""How far a character sees."""
cdef int VIEW_RANGE = 6
"""How far is do the game play. AI move, and do all checks"""
cdef int CHECK_RANGE = 30

"""How many points add when collect blood."""
cdef int ADD_POINTS = 10

"""Guns characteristics"""
cdef int GUN_B_STRONG = 10
cdef int GUN_B_DISTANCE = 2
cdef int GUN_B_BULLETS = 1
cdef int GUN_1_STRONG = 40
cdef int GUN_1_BULLETS = 5
cdef int GUN_1_DISTANCE = 2
cdef int GUN_2_STRONG = 20
cdef int GUN_2_BULLETS = 1
cdef int GUN_2_DISTANCE = VIEW_RANGE - 2
cdef int GUN_3_STRONG = 55
cdef int GUN_3_BULLETS = 6
cdef int GUN_3_DISTANCE = <int>(VIEW_RANGE / 2)
cdef int GUN_E_STRONG = 34
cdef int GUN_E_BULLETS = 3
cdef int GUN_E_DISTANCE = VIEW_RANGE - 1

"""Max bullets 0 - 999"""
cdef int MAX_BULLETS = 666
"""Max health 0 - 999"""
cdef int MAX_HEALTH = 100
"""Bullets in one bullets box"""
cdef int BULLETS_ADD = 20
"""Health in one health box"""
cdef int HEALTH_ADD = 10

"""The base probability of wall.
 
Calculate as p=WALL_BASE_PROBABILITY/(WALL_DIVIDER_BASE^walls-1)

Walls is the count of wall rectangles in the neighbor.

-1 is for decrease probability when no wall in neighbor and increase when 
near is one wall (creatins walls not clumps)"""
cdef double WALL_BASE_PROBABILITY = 0.45

"""Base in divider. The formula described in WALL_BASE_PROBABILITY comment above."""
cdef double WALL_DIVIDER_BASE = 3

cdef struct coords:
    int row_min
    int row_max
    int col_min
    int col_max

cdef class Worldmor:
    """Game"""

    cdef unsigned long long ** map
    cdef int rows
    cdef int cols
    cdef int pos_row
    cdef int pos_col
    cdef int mid_row
    cdef int mid_col

    cdef double bullets_exponent
    cdef double bullets_multiply
    cdef double bullets_max_prob

    cdef double health_exponent
    cdef double health_multiply
    cdef double health_max_prob

    cdef double enemy_start_probability
    cdef double enemy_distance_divider
    cdef double enemy_max_prob

    cdef double guns_exponent
    cdef double guns_multiply
    cdef double guns_max_prob

    cdef int move_flag
    cdef int shoot_flag

    def __cinit__(self, int rows, int random_seed, double bullets_exponent, double bullets_multiply,
                  double bullets_max_prob, double health_exponent, double health_multiply, double health_max_prob,
                  double enemy_start_probability, double enemy_distance_divider, double enemy_max_prob,
                  double guns_exponent, double guns_multiply, double guns_max_prob):
        """Init"""
        srand(random_seed)
        self.bullets_exponent = bullets_exponent
        self.bullets_multiply = bullets_multiply
        self.bullets_max_prob = bullets_max_prob

        self.health_exponent = health_exponent
        self.health_multiply = health_multiply
        self.health_max_prob = health_max_prob

        self.enemy_start_probability = enemy_start_probability
        self.enemy_distance_divider = enemy_distance_divider
        self.enemy_max_prob = enemy_max_prob

        self.guns_exponent = guns_exponent
        self.guns_multiply = guns_multiply
        self.guns_max_prob = guns_max_prob

        self.move_flag = 0
        self.shoot_flag = 0
        cdef int i, j
        self.rows = rows
        self.cols = rows
        self.pos_row = <int> (rows / 2)
        self.pos_col = <int> (rows / 2)
        self.mid_row = <int> (rows / 2)
        self.mid_col = <int> (rows / 2)
        self.map = <unsigned long long **> PyMem_Malloc(self.rows * sizeof(unsigned long long*))

        for i in range(self.rows):
            self.map[i] = <unsigned long long *> PyMem_Malloc(self.cols * sizeof(unsigned long long))
            for j in range(self.cols):
                self.map[i][j] = GRASS
        for i in range(rows):
            for j in range(self.cols):
                self.map[i][j] = self.generate_part_of_map(i, j)
        # Set player character
        self.map[self.pos_row][self.pos_col] = self.to_health(100) + self.to_bullets(20) + \
                                               self.to_direction(1) + self.to_visible(1) + self.to_gun(GUN_B) + PLAYER

    def __dealloc__(self):
        free_mem(self.map, self.rows)

    cdef unsigned long long to_health(self, unsigned long long health):
        """Convert health value to size(code) to save in map."""
        return health * 1000

    cdef unsigned long long get_health(self, unsigned long long health):
        """Get health value from size(code) to number for represent and work."""
        return (<unsigned long long> (health / 1000)) % 1000

    cdef unsigned long long to_bullets(self, unsigned long long bullets):
        """Convert bullets value to size(code) to save in map."""
        return bullets * 1000000

    cdef unsigned long long get_bullets(self, unsigned long long bullets):
        """Get bullets value from size(code) to number for represent and work."""
        return (<unsigned long long> (bullets / 1000000)) % 1000

    cdef unsigned long long to_visible(self, unsigned long long visible):
        """Convert visible value to size(code) to save in map."""
        return visible * 100

    cdef unsigned long long get_visible(self, unsigned long long visible):
        """Get visible value from size(code) to number for represent and work."""
        return (<unsigned long long> (visible / 100)) % 10

    cdef unsigned long long to_direction(self, unsigned long long direction):
        """Convert direction value to size(code) to save in map."""
        return direction * 1000000000

    cdef unsigned long long get_direction(self, unsigned long long direction):
        """Get direction value from size(code) to number for represent and work."""
        return (<unsigned long long> (direction / 1000000000)) % 10

    cdef unsigned long long to_gun(self, unsigned long long gun):
        """Convert gun id value to size(code) to save in map."""
        return gun * <unsigned long long>100000000000

    cdef unsigned long long get_gun(self, unsigned long long gun):
        """Get gun value from size(code) to number for represent and work."""
        return (<unsigned long long> (gun / <unsigned long long>100000000000)) % 100

    cpdef void left(self):
        """Set flag to want move left."""
        self.move_flag = 4

    cpdef void right(self):
        """Set flag to want move right."""
        self.move_flag = 2

    cpdef void up(self):
        """Set flag to want move up."""
        self.move_flag = 1

    cpdef void down(self):
        """Set flag to want move down."""
        self.move_flag = 3

    cpdef void shoot(self):
        """Set shoot flag to want shoot. 1 for shoot before move and 2 for shoot after move."""
        if self.move_flag == 0:
            self.shoot_flag = 1
        else:
            self.shoot_flag = 2

    cpdef int do_one_time_moment(self):
        """Method for doing move or shoot at a given time, for the player or for enemy.
        Flags set between times and actions taken are checked. Even in this step, 
        the AI will make some of their steps.
        """
        # check the set flags

        # shoot before move
        if self.shoot_flag == 1:
            self.do_shoot(self.pos_row, self.pos_col)
        # move and collect
        cdef int move_value = 0
        if self.move_flag == 1:
            move_value = self.do_move(self.pos_row, self.pos_col, self.pos_row - 1, self.pos_col)
            if move_value >= 1:
                self.pos_row -= 1
            self.map[self.pos_row][self.pos_col] += self.to_direction(1) - self.to_direction(
                    self.get_direction(self.map[self.pos_row][self.pos_col]))

        elif self.move_flag == 2:
            move_value = self.do_move(self.pos_row, self.pos_col, self.pos_row, self.pos_col + 1)
            if move_value >= 1:
                self.pos_col += 1
            self.map[self.pos_row][self.pos_col] += self.to_direction(2) - \
                                                        self.to_direction(
                                                            self.get_direction(self.map[self.pos_row][self.pos_col]))
        elif self.move_flag == 3:
            move_value = self.do_move(self.pos_row, self.pos_col, self.pos_row + 1, self.pos_col)
            if move_value >= 1:
                self.pos_row += 1
            self.map[self.pos_row][self.pos_col] += self.to_direction(3) - \
                                                        self.to_direction(
                                                            self.get_direction(self.map[self.pos_row][self.pos_col]))
        elif self.move_flag == 4:
            move_value = self.do_move(self.pos_row, self.pos_col, self.pos_row, self.pos_col - 1)
            if move_value >= 1:
                self.pos_col -= 1
            self.map[self.pos_row][self.pos_col] += self.to_direction(4) - \
                                                        self.to_direction(
                                                            self.get_direction(self.map[self.pos_row][self.pos_col]))
        # shoot after move
        if self.shoot_flag == 2:
            self.do_shoot(self.pos_row, self.pos_col)
        self.recalculate_map_range()
        self.shoot_flag = 0
        self.move_flag = 0
        if move_value == 2:
            return ADD_POINTS
        else:
            return 0
        # TODO: Write AI logic + some level set

    @cython.boundscheck(False)
    cdef void do_shoot(self, int row, int col):
        """Method for doing shoot logic for the one field with player or enemy.
        Check bullets, gun and do shoot logic.
        When kill adds score blood to map.
        
        :param row: row position
        :param col: col position
        """
        # check bullets
        cdef int bullets = self.get_bullets(self.map[self.pos_row][self.pos_col])
        cdef int gun = self.get_gun(self.map[self.pos_row][self.pos_col])
        cdef int down_bullets = self.get_bullets_dec(gun)
        if bullets - down_bullets <= 0: return
        cdef int check_col, row_min, row_max, row_step = 1, col_min, col_max, col_step = 1, code, check_health
        cdef int direction = self.get_direction(self.map[self.pos_row][self.pos_col])
        cdef int kill = 0, br = 0, strong, distance
        # get gun parameters
        self.map[self.pos_row][self.pos_col] -= self.to_bullets(down_bullets)
        strong = self.get_strong(gun)
        distance = self.get_distance(gun)
        # direction of shoot
        distance += 1
        if direction == 1:
            col_min = col
            col_max = col + 1
            row_min = row - 1
            row_max = row - distance
            row_step = -1
            to_col = col
            to_row = row - distance + 1
        elif direction == 2:
            row_min = row
            row_max = row + 1
            col_min = col + 1
            col_max = col + distance
            to_row = row
            to_col = col + distance - 1
        elif direction == 3:
            col_min = col
            col_max = col + 1
            row_min = row + 1
            row_max = row + distance
            to_col = col
            to_row = row + distance - 1
        else:
            row_min = row
            row_max = row + 1
            col_min = col - 1
            col_max = col - distance
            col_step = -1
            to_row = row
            to_col = col - distance + 1
        check_col = col_min
        # check the bullet trajectory
        while row_min != row_max:
            col_min = check_col
            while col_min != col_max:
                code = self.map[row_min][col_min] % 100
                if code == WALL:
                    check_health = self.get_health(self.map[row_min][col_min]) - strong
                    if check_health < 0:
                        kill = 2
                    else:
                        self.map[row_min][col_min] -= self.to_health(strong)
                    row_min += row_step
                    col_min += col_step
                    br = 1
                    break
                if code == PLAYER:
                    check_health = self.get_health(self.map[row_min][col_min]) - strong
                    if check_health < 0:
                        kill = 1
                    else:
                        self.map[row_min][col_min] -= self.to_health(strong)
                    row_min += row_step
                    col_min += col_step
                    br = 1
                    break
                if ENEMY_E >= code >= ENEMY_B:
                    check_health = self.get_health(self.map[row_min][col_min]) - strong
                    if check_health < 0:
                        kill = 1
                    else:
                        self.map[row_min][col_min] -= self.to_health(strong)
                    row_min += row_step
                    col_min += col_step
                    br = 1
                    break
                col_min += col_step
            if br == 1:
                break
            row_min += row_step
        if kill == 1:
            # add blood to map to can collect points after kill enemies
            self.map[row_min-row_step][col_min-col_step] = self.to_visible(1) + BLOOD
        elif kill == 2:
            # no blood after kill wall
            self.map[row_min-row_step][col_min-col_step] = self.to_visible(1) + GRASS
        else:
            # add shoot explosion for some time
            self.map[row_min-row_step][col_min-col_step] += \
                self.to_visible(9 - self.get_visible(self.map[row_min-row_step][col_min-col_step]))

    cdef int get_strong(self, int gun):
        """Return gun strong based on the gun code."""
        if gun == GUN_E:
            return GUN_E_STRONG
        elif gun == GUN_1:
            return GUN_1_STRONG
        elif gun == GUN_2:
            return GUN_2_STRONG
        elif gun == GUN_3:
            return GUN_3_STRONG
        else:
            return GUN_B_STRONG

    cdef int get_distance(self, int gun):
        """Return gun range of shoot based on the gun code."""
        if gun == GUN_E:
            return GUN_E_DISTANCE
        elif gun == GUN_1:
            return GUN_1_DISTANCE
        elif gun == GUN_2:
            return GUN_2_DISTANCE
        elif gun == GUN_3:
            return GUN_3_DISTANCE
        else:
            return GUN_B_DISTANCE

    cdef int get_bullets_dec(self, int gun):
        """Return gun bullet cost based on the gun code."""
        if gun == GUN_E:
            return GUN_E_BULLETS
        elif gun == GUN_1:
            return GUN_1_BULLETS
        elif gun == GUN_2:
            return GUN_2_BULLETS
        elif gun == GUN_3:
            return GUN_3_BULLETS
        else:
            return GUN_B_BULLETS

    @cython.boundscheck(False)
    cdef int do_move(self, int old_row, int old_col, int new_row, int new_col):
        """Method to perform moves at a given position, 
        the movement is performed if there is no other character or wall. 
        Also, some items may be collected.
        
        :param old_row: previous row position
        :param old_col: previous columns position
        :param new_row: new row position
        :param new_col: new column position
        :return: 1 if the character rolls or 0 if not.
        """
        cdef int code
        cdef int do = 0
        cdef unsigned long long add = 0

        code = self.map[new_row][new_col] % 100
        # check code of new field and do the steps for the character
        if code == GRASS or code == BLOOD:
            do = 1
        if code == HEALTH:
            do = 1
            add = self.to_health(min((<int>self.get_health(self.map[old_row][old_col])) +
                                     HEALTH_ADD, MAX_HEALTH)-self.get_health(self.map[old_row][old_col]))

        if code == BULLET:
            do = 1
            add = self.to_bullets(min((<int>self.get_bullets(self.map[old_row][old_col])) +
                                     BULLETS_ADD, MAX_BULLETS)-self.get_bullets(self.map[old_row][old_col]))
        if code == GUN_B:
            do = 1
            add = self.to_gun(GUN_B - self.get_gun(self.map[old_row][old_col]))
        if code == GUN_1:
            do = 1
            add = self.to_gun(GUN_1 - self.get_gun(self.map[old_row][old_col]))
        if code == GUN_2:
            do = 1
            add = self.to_gun(GUN_2 - self.get_gun(self.map[old_row][old_col]))
        if code == GUN_3:
            do = 1
            add = self.to_gun(GUN_3 - self.get_gun(self.map[old_row][old_col]))
        if code == GUN_E:
            do = 1
            add = self.to_gun(GUN_E - self.get_gun(self.map[old_row][old_col]))
        if do == 1:
            self.map[new_row][new_col] = self.map[old_row][old_col] + add
            self.map[old_row][old_col] = 0 + self.to_visible(1)
            if code == BLOOD: return 2
            else: return 1
        return 0

    @cython.boundscheck(False)
    cdef void recalculate_map_range(self):
        """Check specific map range and check visibilities, 
        find enemy and do their AI steps. 
        Manage visibility of the map. 
        """
        cdef int row, col
        cdef double distance
        cdef unsigned long long visibility
        # Calculate possibly range where can change the visibility
        for row in range(self.pos_row - CHECK_RANGE, self.pos_row + CHECK_RANGE + 1):
            for col in range(self.pos_col - CHECK_RANGE, self.pos_col + CHECK_RANGE + 1):
                if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
                    continue
                distance = sqrt(abs(row - self.pos_row) ** 2 + abs(col - self.pos_col) ** 2)
                visibility = self.get_visible(self.map[row][col])
                if visibility > 3:
                    self.map[row][col] -= self.to_visible(1)
                if visibility == 3:
                    self.map[row][col] -= self.to_visible(2)
                if distance < VIEW_RANGE:  # if could see
                    if visibility == 2: # Player see this field
                        self.map[row][col] -= self.to_visible(1)
                    if visibility == 0: # Player dont see this field
                        self.map[row][col] += self.to_visible(1)
                else: # could not see do it in "fog"
                    if visibility == 1:
                        self.map[row][col] += self.to_visible(1)

    @cython.wraparound(False)
    @cython.boundscheck(False)
    cpdef np.ndarray[np.int64_t, ndim=2] get_map(self, int row, int col):
        """Method for obtaining and creating a viewport from the map to be displayed.
        The center of map is always player.

        :param row: number of rows to display
        :param col: number of columns to display
        :return: a part of global map with values
        """
        cdef int i, j
        cdef np.ndarray[np.int64_t, ndim=2] map_view = np.zeros((row, col), dtype=np.int64)
        cdef coords co = self.get_cords_slides(row, col)

        if co.col_min < 1:
            self.refactor_cols_down()
            co = self.get_cords_slides(row, col)
        if co.col_max >= self.cols:
            self.refactor_cols_up()
            co = self.get_cords_slides(row, col)
        if co.row_min < 1:
            self.refactor_rows_down()
            co = self.get_cords_slides(row, col)
        if co.row_max >= self.rows:
            self.refactor_rows_up()
            co = self.get_cords_slides(row, col)

        for i in range(row):
            for j in range(col):
                map_view[i, j] = self.map[co.row_min + i][co.col_min + j]
        return map_view

    @cython.cdivision(True)
    @cython.boundscheck(False)
    cdef unsigned long long generate_part_of_map(self, int row, int column):
        """Function for generating a map based on some probabilities to add specific items or walls.
        
        :param row: row position to generate to map
        :param column: column position to generate to map 
        :return: 
        """
        # Not do garbage near player.
        cdef int walls = self.count_near_walls(row, column)
        cdef double distance = sqrt(abs(row - self.mid_row) ** 2 + abs(column - self.mid_col) ** 2)
        cdef unsigned long long to_set
        if distance < VIEW_RANGE:
            to_set = self.to_visible(1)
        else:
            to_set = self.to_visible(0)
        if abs(row - self.pos_row) < STARTING_PROTECTION_ZONE \
                and abs(column - self.pos_col) < STARTING_PROTECTION_ZONE:
            return to_set + GRASS

        if (rand() / <float> RAND_MAX) < (WALL_BASE_PROBABILITY / (WALL_DIVIDER_BASE ** abs(walls - 1))):
            return to_set + self.to_health(100) + WALL

        if (rand() / <float> RAND_MAX) < min(self.bullets_max_prob,
                                             (1 / (distance ** self.bullets_exponent)) * self.bullets_multiply):
            return to_set + BULLET

        if (rand() / <float> RAND_MAX) < min(self.health_max_prob,
                                             (1 / (distance ** self.health_exponent)) * self.health_multiply):
            return to_set + HEALTH

        if (rand() / <float> RAND_MAX) < min(self.enemy_max_prob,
                                             self.enemy_start_probability * (distance / self.enemy_distance_divider)):
            return to_set + self.to_health(100) + self.to_bullets(20)+ self.to_gun(GUN_B) + \
                   ((rand() % (ENEMY_E - ENEMY_B)) + ENEMY_B + 1)

        if (rand() / <float> RAND_MAX) < min(self.guns_max_prob,
                                             (1 / (distance ** self.guns_exponent)) * self.guns_multiply):
            return to_set + ((rand() % (GUN_E - GUN_B)) + GUN_B + 1)

        return to_set + 0

    @cython.cdivision(True)
    @cython.boundscheck(False)
    cdef int count_near_walls(self, int row, int column):
        """Count number of walls in the neighborhood.
        
        :param row: row position on map
        :param column: column position on map
        :return: number of walls
        """

        cdef int i, j, rows, cols, walls = 0
        for i in range(-1, 2):
            rows = row + i
            if rows < 0 or rows >= self.rows:
                continue
            for j in range(-1, 2):
                if j == 0 and i == 0:
                    continue
                cols = column + j
                if cols < 0 or cols >= self.cols:
                    continue
                if self.map[rows][cols] % 100 == 1:
                    walls += 1
        return walls

    cdef void refactor_cols_up(self):
        """If the map end is reached in the columns to the right(direction) | up(array representation), 
        the method will reallocate the map so that it creates a double size of the map and generates the map.
        """
        cdef int new_cols = self.cols * 2
        cdef unsigned long long *tmp
        cdef int i, j

        for i in range(self.rows):
            tmp = <unsigned long long *> PyMem_Malloc(new_cols * sizeof(unsigned long long))
            # first part is same
            for j in range(self.cols):
                tmp[j] = self.map[i][j]
            # new second part is need to generate
            for j in range(self.cols, new_cols, 1):
                tmp[j] = self.generate_part_of_map(i, j)
            PyMem_Free(self.map[i])
            self.map[i] = tmp
        self.cols = new_cols

    cdef void refactor_cols_down(self):
        """If the map end is reached in the columns to the left(direction)| down(array representation), 
        the method will reallocate the map so that it creates a double size of the map and generates the map.
        The new part of map is created from 0, it needs shift data and shift the position of the player.
        """
        cdef int new_cols = self.cols * 2
        cdef unsigned long long *tmp
        cdef int i, j
        self.mid_col += self.cols
        for i in range(self.rows):
            tmp = <unsigned long long *> PyMem_Malloc(new_cols * sizeof(unsigned long long))
            # first part need to generate, down reach..
            for j in range(self.cols):
                tmp[j] = self.generate_part_of_map(i, j)
            # the next part only copy
            for j in range(self.cols, new_cols, 1):
                tmp[j] = self.map[i][j - self.cols]
            PyMem_Free(self.map[i])
            self.map[i] = tmp
        self.pos_col += self.cols
        self.cols = new_cols

    cdef void refactor_rows_down(self):
        """If the map end is reached in the rows to the up(direction)| down(array representation), 
        the method will reallocate the map so that it creates a double size of the map and generates the map.
        The new part of map is created from 0, it needs shift data and shift the position of the player.
        """
        cdef int new_rows = self.rows * 2
        cdef unsigned long long ** tmp
        cdef int i, j
        self.mid_row += self.rows
        tmp = <unsigned long long **> PyMem_Malloc(new_rows * sizeof(unsigned long long*))
        # first part need to generate, down reach..
        for i in range(self.rows):
            tmp[i] = <unsigned long long *> PyMem_Malloc(self.cols * sizeof(unsigned long long))
            for j in range(self.cols):
                tmp[i][j] = self.generate_part_of_map(i, j)
        # the next part only copy
        for i in range(self.rows, new_rows, 1):
            tmp[i] = self.map[i - self.rows]
        PyMem_Free(self.map)
        self.map = tmp
        self.pos_row += self.rows
        self.rows = new_rows

    cdef void refactor_rows_up(self):
        """If the map end is reached in the rows to the down(direction)| up(array representation), 
        the method will reallocate the map so that it creates a double size of the map and generates the map.
        """
        cdef int new_rows = self.rows * 2
        cdef unsigned long long ** tmp
        cdef int i, j
        tmp = <unsigned long long **> PyMem_Malloc(new_rows * sizeof(unsigned long long*))
        # first part is same
        for i in range(self.rows):
            tmp[i] = self.map[i]
        # new second part is need to generate
        for i in range(self.rows, new_rows, 1):
            tmp[i] = <unsigned long long *> PyMem_Malloc(self.cols * sizeof(unsigned long long))
            for j in range(self.cols):
                tmp[i][j] = self.generate_part_of_map(i, j)
        PyMem_Free(self.map)
        self.map = tmp
        self.rows = new_rows

    @cython.nonecheck(False)
    @cython.cdivision(True)
    cdef coords get_cords_slides(self, int row, int col):
        """Method that determines the coordinates of the saved map to be displayed for the specified map size.
        
        :param row: number of row to display
        :param col: number of columns to display
        :return: min and max coordinates for both direction as structure
        """
        cdef int x1, x2, y1, y2
        x1 = self.pos_row - (row - 1) / 2
        x2 = self.pos_row + row / 2 + 1
        y1 = self.pos_col - (col - 1) / 2
        y2 = self.pos_col + col / 2 + 1
        return coords(x1, x2, y1, y2)

@cython.boundscheck(False)
cdef void free_mem(unsigned long long ** array, int length):
    """Free allocated memory using malloc.
    
    :param array: 2D array to free
    :param length: length of first dimension
    """
    for i in range(length):
        PyMem_Free(array[i])
    PyMem_Free(array)
