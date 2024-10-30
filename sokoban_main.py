import sokoban_console_refactored as skb
from bfs import BFSSolver

g = skb.Sokoban("input.txt")
g.draw_input_matrix()

bfs = BFSSolver(g)
print(bfs.solve())