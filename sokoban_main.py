import sokoban_console_refactored as skb
from bfs import BFSSolver
from dfs import DFSSolver
from ucs import UCSSolver
from astar import AStarSolver
import time as time

g = skb.Sokoban("input.txt")
g.draw_input_matrix()

for algo in ["astar"]:
    solver = None
    if algo == "bfs":
        solver = BFSSolver(g)
    elif algo == "dfs":
        solver = DFSSolver(g)
    elif algo == "ucs":
        solver = UCSSolver(g)
    else: # astar
        solver = AStarSolver(g)
    print("Solving with ", algo, "-"*20)
    start = time.time()
    path = solver.solve()
    end = time.time()
    print("Path: ", path)
    print("Time: ", end-start)
    print("Running ... ")
    g.run(path)