from bfs import BFSSolver
from dfs import DFSSolver
from ucs import UCSSolver
from astar import AStarSolver
from sokoban import Sokoban
from runner import Runner
import os

INPUT_DIR = "input"
OUTPUT_DIR = "output"

for file in os.listdir(INPUT_DIR):
    if file.startswith("input_") and file.endswith(".txt"):
        g = Sokoban(f"{INPUT_DIR}/{file}")
        output_file = file.replace("input_", "output_")
        with open(f"{OUTPUT_DIR}/{output_file}", "w") as f:
            for algo in ["BFS", "DFS", "UCS", "AStar"]:
                print(f"Running {algo} on {file}")
                if algo == "BFS":
                    solver = BFSSolver(g)
                elif algo == "DFS":
                    solver = DFSSolver(g)
                elif algo == "UCS":
                    solver = UCSSolver(g)
                elif algo == "AStar":
                    solver = AStarSolver(g)
                path = solver.solve()
                f.write(algo + "\n")
                if path is None:
                    f.write("No solution\n")
                else:
                    print(solver.record.data())
                    f.write(solver.record.data() + "\n")
            #result = Runner.run(g, path)
            #print(result)

# g = Sokoban("input/input_1.txt")

# bfs = BFSSolver(g)
# dfs = DFSSolver(g)
# ucs = UCSSolver(g)
# astar = AStarSolver(g)
# g.draw_state(g.matrix)
# path = dfs.solve()
# print(path)
# print(dfs.record.data())