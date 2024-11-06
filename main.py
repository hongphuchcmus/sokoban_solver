from bfs import BFSSolver
from dfs import DFSSolver
from ucs import UCSSolver
from astar import AStarSolver
from sokoban import Sokoban, Record
from runner import Runner
import os
import psutil

INPUT_DIR = "input"
OUTPUT_DIR = "output"

solver_records = {}
for file in os.listdir(INPUT_DIR):
    if file.startswith("input-") and file.endswith(".txt"):
        g = Sokoban(f"{INPUT_DIR}/{file}")
        for algo in ["BFS", "DFS", "UCS", "AStar"]:
            if algo == "BFS":
                solver = BFSSolver(g)
            elif algo == "DFS":
                solver = DFSSolver(g)
            elif algo == "UCS":
                solver = UCSSolver(g)
            elif algo == "AStar":
                solver = AStarSolver(g)
            
            solver.solve()
            if algo not in solver_records:
                solver_records[algo] = []
            solver_records[algo].append(solver.record)

# Write a csv
# Time
# Map/Algo | 1 | 2 | 3 | 4 | ... | n
# BFS      |   |   |   |   |     |  
# DFS      |   |   |   |   |     |  
# UCS      |   |   |   |   |     |  
# AStar    |   |   |   |   |     |  

with open("output.csv", "w") as f:
    f.write("Property, Algorithm")
    for i in range(len(solver_records["BFS"])):
        f.write(f",\"{i+1}\"")
    f.write("\n")

    for prop in ["Time", "Steps", "Node", "Memory usage"]:
        for algo in solver_records:
            f.write(f"{prop}")
            f.write(f", {algo}")
            for record in solver_records[algo]:
                if prop == "Time":
                    f.write(f",{record.time_ms}")
                elif prop == "Steps":
                    f.write(f",{record.steps}")
                elif prop == "Node":
                    f.write(f",{record.node}")
                elif prop == "Memory usage":
                    f.write(f",{record.memory_mb}")
            f.write("\n")