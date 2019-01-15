#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
import numpy as np

cimport numpy as np
cimport cython

from cpython.mem cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free
from libc.stdlib cimport rand, RAND_MAX


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

    def __cinit__(self, int rows, int cols, int pos_row, int pos_col):
        """Init"""
        cdef int i, j
        self.rows = rows
        self.cols = cols
        self.pos_row = pos_row
        self.pos_col = pos_col
        self.map = <int **> PyMem_Malloc(self.rows*sizeof(int*))
        for i in range(rows):
            self.map[i] = <int *> PyMem_Malloc(self.cols*sizeof(int))
            for j in range(cols):
                # TODO: need generate map base on some probability (no cycle of wall check)
                self.map[i][j] = (rand() % 3) + 1

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
                    map_view[i, j] = 0
                else:
                    map_view[i, j] = self.map[co.row_min+i][co.col_min+j]
        return map_view

    cdef void refactor_cols_up(self):
        """
        If the map end is reached in the columns to the right(direction) | up(array representation), 
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
                # TODO: need generate map base on some probability (no cycle of wall check)
                tmp[j] = (rand() % 3) + 1
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
                tmp[j] = (rand() % 3) + 1
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
                tmp[i][j] = (rand() % 3) + 1
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
                # TODO: need generate map base on some probability (no cycle of wall check)
                tmp[i][j] = (rand() % 3) + 1
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
