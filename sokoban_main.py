import sokoban_console_refactored as skb
from bfs import BFSSolver
from dfs import DFSSolver
from ucs import UCSSolver
from astar import AStarSolver
import time as time
import tracemalloc as tracemalloc
import sys

g = skb.Sokoban("input.txt")
g.draw_input_matrix()

for algo in ["bfs", "dfs", "ucs", "astar"]:
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
    path = solver.solve()
    print("Record:", solver.record)
    g.run(path, False)