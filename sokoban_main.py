import sokoban_console_refactored as skb
from bfs import BFSSolver
from dfs import DFSSolver
from ucs import UCSSolver
import time as time

g = skb.Sokoban("input.txt")
g.draw_input_matrix()

for algo in ["bfs", "dfs", "ucs"]:
    solver = None
    if algo == "bfs":
        solver = BFSSolver(g)
    elif algo == "dfs":
        solver = DFSSolver(g)
    else: # algo == "ucs":
        solver = UCSSolver(g)
    print("Solving with ", algo, "-"*20)
    start = time.time()
    path = solver.solve()
    end = time.time()
    print("Path: ", path)
    print("Time: ", end-start)
    print("Running ... ")
    g.run(path)