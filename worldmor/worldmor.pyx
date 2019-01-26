#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
import numpy as np

cimport numpy as np
cimport cython

from cpython.mem cimport PyMem_Malloc, PyMem_Free
from libc.stdlib cimport rand, RAND_MAX

cpdef enum:
    # Enum for items, players and environments of the map.
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

cdef struct coords:
    int row_min
    int row_max
    int col_min
    int col_max


# TODO: Write game logic
cdef class Worldmor:
    """Game"""

    cdef int ** map
    cdef int rows
    cdef int cols
    cdef int pos_row
    cdef int pos_col
    cdef int mid_row
    cdef int mid_col

    def __cinit__(self, int rows):
        """Init"""
        cdef int i, j
        self.rows = rows
        self.cols = rows
        self.pos_row = <int>(rows/2)
        self.pos_col = <int>(rows/2)
        self.mid_row = <int>(rows/2)
        self.mid_col = <int>(rows/2)
        self.map = <int **> PyMem_Malloc(self.rows*sizeof(int*))
        for i in range(self.rows):
            self.map[i] = <int *> PyMem_Malloc(self.cols*sizeof(int))
            for j in range(self.cols):
                self.map[i][j] = GRASS
        for i in range(rows):
            for j in range(self.cols):
                self.map[i][j] = self.generate_part_of_map(i, j)

    def __dealloc__(self):
        free_mem(self.map, self.rows)

    cpdef void left(self):
        self.pos_col -= 1

    cpdef void right(self):
        self.pos_col += 1

    cpdef void up(self):
        self.pos_row -= 1

    cpdef void down(self):
        self.pos_row += 1

    @cython.wraparound(False)
    @cython.boundscheck(False)
    cpdef np.ndarray[np.int64_t, ndim=2] get_map(self, int row, int col):
        """
        Method for obtaining and creating a viewport from the map to be displayed.
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
                if co.row_min+i == self.pos_row and co.col_min+j == self.pos_col:
                    map_view[i, j] = PLAYER
                else:
                    map_view[i, j] = self.map[co.row_min+i][co.col_min+j]
        return map_view

    @cython.cdivision(True)
    @cython.boundscheck(False)
    cdef int generate_part_of_map(self, int row, int column):
        """Function for generating a map based on some probabilities to add specific items or walls.
        
        :param row: row position to generate to map
        :param column: column position to generate to map 
        :return: 
        """

        # Not do garbage near player.
        cdef int walls = self.count_near_walls(row, column)
        # TODO: From MID post can compute euclidean distance from the previous middle and shoot down probability to hard the game
        if abs(row - self.pos_row) < 4 and abs(column - self.pos_col) < 4:
            return GRASS
        if (rand()/<float>RAND_MAX) < (0.45/(3**abs(walls-1))):
            return WALL
        if (rand()/<float>RAND_MAX) < 0.03:
            return BULLET
        if (rand()/<float>RAND_MAX) < 0.01:
            return HEALTH
        if (rand()/<float>RAND_MAX) < 0.01:
            return (rand() % (ENEMY_E-ENEMY_B)) + ENEMY_B + 1
        if (rand()/<float>RAND_MAX) < 0.01:
            return (rand() % (GUN_E-GUN_B)) + GUN_B + 1
        return 0

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
            rows = row+i
            if rows < 0 or rows >= self.rows:
                continue
            for j in range(-1, 2):
                if j == 0 and i == 0:
                    continue
                cols = column+j
                if cols < 0 or cols >= self.cols:
                    continue
                if self.map[rows][cols] == 1:
                    walls += 1
        return walls

        the method will reallocate the map so that it creates a double size of the map and generates the map.
        """
        cdef int new_cols = self.cols * 2
        cdef int * tmp
        cdef int i, j

        for i in range(self.rows):
            tmp = <int *> PyMem_Malloc(new_cols*sizeof(int))
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
        """
        If the map end is reached in the columns to the left(direction)| down(array representation), 
        the method will reallocate the map so that it creates a double size of the map and generates the map.
        The new part of map is created from 0, it needs shift data and shift the position of the player.
        """
        cdef int new_cols = self.cols * 2
        cdef int * tmp
        cdef int i, j

        for i in range(self.rows):
            tmp = <int *> PyMem_Malloc(new_cols*sizeof(int))
            # first part need to generate, down reach..
            for j in range(self.cols):
                # TODO: need generate map base on some probability (no cycle of wall check)
                tmp[j] = (rand() % 3)
            # the next part only copy
            for j in range(self.cols, new_cols, 1):
                tmp[j] = self.map[i][j-self.cols]
            PyMem_Free(self.map[i])
            self.map[i] = tmp
        self.pos_col += self.cols
        self.cols = new_cols

    cdef void refactor_rows_down(self):
        """
        If the map end is reached in the rows to the up(direction)| down(array representation), 
        the method will reallocate the map so that it creates a double size of the map and generates the map.
        The new part of map is created from 0, it needs shift data and shift the position of the player.
        """
        cdef int new_rows = self.rows * 2
        cdef int ** tmp
        cdef int i, j
        tmp = <int **> PyMem_Malloc(new_rows*sizeof(int*))
        # first part need to generate, down reach..
        for i in range(self.rows):
            tmp[i] = <int *> PyMem_Malloc(self.cols*sizeof(int))
            for j in range(self.cols):
                # TODO: need generate map base on some probability (no cycle of wall check)
                tmp[i][j] = (rand() % 3)
        # the next part only copy
        for i in range(self.rows, new_rows, 1):
            tmp[i] = self.map[i-self.rows]
        PyMem_Free(self.map)
        self.map = tmp
        self.pos_row += self.rows
        self.rows = new_rows

    cdef void refactor_rows_up(self):
        """
        If the map end is reached in the rows to the down(direction)| up(array representation), 
        the method will reallocate the map so that it creates a double size of the map and generates the map.
        """
        cdef int new_rows = self.rows * 2
        cdef int ** tmp
        cdef int i, j
        tmp = <int **> PyMem_Malloc(new_rows*sizeof(int*))
        # first part is same
        for i in range(self.rows):
            tmp[i] = self.map[i]
        # new second part is need to generate
        for i in range(self.rows, new_rows, 1):
            tmp[i] = <int *> PyMem_Malloc(self.cols*sizeof(int))
            for j in range(self.cols):
                tmp[i][j] = self.generate_part_of_map(i, j)
        PyMem_Free(self.map)
        self.map = tmp
        self.rows = new_rows

    @cython.nonecheck(False)
    @cython.cdivision(True)
    cdef coords get_cords_slides(self, int row, int col):
        """
        Method that determines the coordinates of the saved map to be displayed for the specified map size.
        
        :param row: number of row to display
        :param col: number of columns to display
        :return: min and max coordinates for both direction as structure
        """
        cdef int x1, x2, y1, y2
        x1 = self.pos_row - (row-1)/2
        x2 = self.pos_row + row/2 + 1
        y1 = self.pos_col - (col-1)/2
        y2 = self.pos_col + col/2 + 1
        return coords(x1, x2, y1, y2)


@cython.boundscheck(False)
cdef void free_mem(int ** array, int length):
    for i in range(length):
        PyMem_Free(array[i])
    PyMem_Free(array)
