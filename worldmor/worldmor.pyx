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

    @cython.wraparound(False)
    @cython.boundscheck(False)
    cpdef np.ndarray[np.int64_t, ndim=2] get_map(self, int row, int col):
        """Return map"""
        cdef int i, j
        cdef np.ndarray[np.int64_t, ndim=2] map_view = np.zeros((row, col), dtype=np.int64)
        cdef coords co = self.get_cords_slides(row, col)
        #print(co)
        if co.col_min < 1 or co.col_max >= self.cols:
            print("need add cols")
        if co.row_min < 1 or co.row_max >= self.rows:
            print("need add rows")
        # TODO: check if is to big or small it is need resize (some magic)
        for i in range(row):
            for j in range(col):
                if co.row_min+i == self.pos_row and co.col_min+j == self.pos_col:
                    self.map[i][j] = 0
                else:
                    map_view[i, j] = self.map[co.row_min+i][co.col_min+j]
        return map_view

    @cython.nonecheck(False)
    @cython.cdivision(True)
    cdef coords get_cords_slides(self, int x, int y):
        cdef int x1, x2, y1, y2
        x1 = self.pos_row - (x-1)/2
        x2 = self.pos_row + x/2 + 1
        y1 = self.pos_col - (y-1)/2
        y2 = self.pos_col + y/2 + 1
        return coords(x1, x2, y1, y2)

    cpdef void left(self):
        self.pos_col -= 1

    cpdef void right(self):
        self.pos_col += 1

    cpdef void up(self):
        self.pos_row -= 1

    cpdef void down(self):
        self.pos_row += 1


@cython.boundscheck(False)
cdef void free_mem(int ** array, int length):
    for i in range(length):
        PyMem_Free(array[i])
    PyMem_Free(array)
