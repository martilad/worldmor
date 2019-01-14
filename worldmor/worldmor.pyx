import numpy as np
cimport numpy as np

# TODO: Write game logic
cdef class Worldmor:
    """Game"""

    cpdef np.ndarray[np.int64_t, ndim=2] get_map(self, int x, int y):
        """Method for get part of global map, specific by size"""
        return np.zeros((x, y), dtype=np.uint8)