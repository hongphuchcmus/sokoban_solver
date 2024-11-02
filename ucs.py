from sokoban import WALL, ARES, STONE, SPACE, SWITCH, ARES_ON_SWITCH, STONE_ON_SWITCH, Sokoban, Record
from heapq import heappop, heappush, heapify
import time
import tracemalloc
import os
from solver_utils import can_move, is_deadlock, init_state, is_solved

class UCSSolver:
    def __init__(self, g : Sokoban) -> None:
        self.frontier = []
        self.explored = {None}
        self.g = g
        self.stone_weights = {}

        self.record = Record()

    def solve(self):
        self.record.steps = 0
        self.record.node = 1
        start_time = time.time()
        tracemalloc.start()
        #mem_before = Record.process_memory()

        g = self.g
        self.frontier = []
        self.explored = {None}
        initial_state, self.stone_weights = init_state(g)
        # (path_cost, state, ares_pos, path)
        self.frontier = [(0, initial_state, g.to_pos_2d(g.ares_pos), '')]
        self.explored.clear()

        result = None

        moves = Sokoban.moves()
        while self.frontier:
            #self.frontier.sort(key = lambda x: x[0])
            curr_cost, state, ares_pos, path = heappop(self.frontier)
            self.explored.add(state)

            if is_solved(state):
                result = (curr_cost, path)
                break

            for move in moves:
                new_state, move_cost, pushed = can_move(g, state, ares_pos, move, self.stone_weights)
                if new_state is None or new_state in self.explored or is_deadlock(g, new_state):
                    continue

                new_cost = curr_cost + move_cost
                
                frontier_pos = next((i for i, f in enumerate(self.frontier) if f[2] == new_state), -1)

                if frontier_pos == -1 or new_cost < self.frontier[frontier_pos][0]:
                    path_dir =  Sokoban.move_to_char(move).upper() if pushed else Sokoban.move_to_char(move)
                    new_ares_pos = (ares_pos[0] + move[0], ares_pos[1] + move[1])
                    
                    if frontier_pos != -1:
                        self.frontier[frontier_pos] = self.frontier[-1]
                        self.frontier.pop()
                        heapify(self.frontier)
                    heappush(self.frontier, (new_cost, new_state, new_ares_pos, path + path_dir))
                    self.record.node += 1

        if result == None:
            return None
        
        self.record.time_ms = (time.time() - start_time) * 1000
        self.record.memory_mb = tracemalloc.get_traced_memory()[1] / (1024**2)#(Record.process_memory() - mem_before) / 1024**2 # B -> MiB #tracemalloc.get_traced_memory()[1] / 1000
        tracemalloc.stop()
        self.record.weight = result[0] - len(result[1])
        self.record.steps = len(result[1])
        
        return result[1]
