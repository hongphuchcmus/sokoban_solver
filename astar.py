from sokoban import WALL, ARES, STONE, SPACE, SWITCH, ARES_ON_SWITCH, STONE_ON_SWITCH, Sokoban, Record
from heapq import heappop, heappush, heapify
import time
import tracemalloc
import os
from bfs import BFSSolver

from solver_utils import can_move, is_deadlock, init_state, is_solved, get_stones

class AStarSolver:
    def __init__(self, g : Sokoban) -> None:
        self.frontier = []
        self.explored = {None}
        self.g = g
        self.stone_weights = {}
        self.timeout = False
        self.record = Record()


    def manhattan_distance(self, state):
        g = self.g
        stones = get_stones(g, state)
        cost = 0
        assigned = set()
        for stone in stones:
            min_cost = float('inf')
            min_switch = g.switch_pos[0]
            for i in range(len(g.switch_pos)):
                if i in assigned:
                    continue
                switch = g.to_pos_2d(g.switch_pos[i])
                c = abs(stone[0] - switch[0]) + abs(stone[1] - switch[1])
                if c < min_cost:
                    min_cost = c
                    min_switch = i
            assigned.add(min_switch)
            cost += min_cost
        return cost
    
    def solve(self, recorded = True, timeout = -1, record_memory = True):
        g = self.g
        start_time = time.time()
        # Set up record
        if recorded:
            self.record.steps = 0
            self.record.node = 1
            self.record.memory_mb = 0
            if record_memory:
                tracemalloc.start()
        # Reset timeout
        self.timeout = False

        g = self.g
        self.frontier = []
        self.explored = {None}
        initial_state, self.stone_weights = init_state(g)
        # (fcost, gcost, state, ares_pos, path)
        self.frontier = [(self.manhattan_distance(g.matrix), 0, initial_state, g.to_pos_2d(g.ares_pos), '')]
        self.explored.clear()

        result = None

        moves = Sokoban.moves()
        while self.frontier:
            if timeout != -1 and time.time() - start_time > timeout:
                print(f"Timeout! {timeout}s")
                self.timeout = True
                return None
            
            _, curr_gcost, state, ares_pos, path = heappop(self.frontier)
            self.explored.add(state)

            if is_solved(state):
                result = (curr_gcost, path)
                break

            for move in moves:
                new_state, move_cost, pushed = can_move(g, state, ares_pos, move, self.stone_weights)
                if new_state is None or new_state in self.explored or is_deadlock(g, new_state):
                    continue

                gcost = curr_gcost + move_cost
                fcost = gcost + self.manhattan_distance(state)
                
                frontier_pos = next((i for i, f in enumerate(self.frontier) if f[2] == new_state), -1)

                if frontier_pos == -1 or gcost < self.frontier[frontier_pos][1]:
                    path_dir =  Sokoban.move_to_char(move).upper() if pushed else Sokoban.move_to_char(move)
                    new_ares_pos = (ares_pos[0] + move[0], ares_pos[1] + move[1])
                    
                    if frontier_pos != -1:
                        self.frontier[frontier_pos] = self.frontier[-1]
                        self.frontier.pop()
                        # Tried this but the speed improvement is mininal
                        # if frontier_pos < len(self.frontier):
                        #     _siftup(self.frontier, frontier_pos)
                        #     _siftdown(self.frontier, 0, frontier_pos)
                        heapify(self.frontier)
                    heappush(self.frontier, (fcost, gcost, new_state, new_ares_pos, path + path_dir))
                    
                    if recorded:
                        self.record.node += 1

        if result == None:
            return None
        
        if recorded:
            self.record.time_ms = (time.time() - start_time) * 1000
            if record_memory:
                self.record.memory_mb = tracemalloc.get_traced_memory()[1] / 1024**2
                tracemalloc.stop()
            self.record.weight = result[0] - len(result[1])
            self.record.steps = len(result[1])
        
        return result[1]
