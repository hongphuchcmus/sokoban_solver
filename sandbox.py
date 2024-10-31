import time as time

a_1 = ((1, 2), ((6, 3), (2, 7), (19, -1), (7, 24), (5, 8)))
a_2 = [(1, 2), [(6, 3), (2, 7), (19, -1), (7, 24), (5, 8)]]

start = time.time()
for i in range(1000000):
    b = list(a_1[1])
    b[2] = (7, -4)
    c = ((1, 2), tuple(b))
print("Time for tuples: ", time.time() - start)

start = time.time()
for i in range(1000000):
    b = a_2[1].copy()
    b[2] = (7, -4)
    c = [(1, 2), b]
print("Time for lists: ", time.time() - start)
