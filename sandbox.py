import time as time
import sys as sys

a_1 = ((1, 2), ((6, 3), (2, 7), (19, -1), (7, 24), (5, 8)))
a_2 = [(1, 2), [(6, 3), (2, 7), (19, -1), (7, 24), (5, 8)]]

s = sys.getsizeof(a_2)
print(tuple(a_2))