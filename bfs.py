from sokoban import WALL, ARES, STONE, SPACE, SWITCH, ARES_ON_SWITCH, STONE_ON_SWITCH, Sokoban, Record
import time 
import tracemalloc
import sys
from solver_utils import can_move, is_deadlock, init_state, is_solved


class BFSSolver:
    def __init__(self, g : Sokoban) -> None:
        self.frontier = []
        self.explored = {None}
        self.stone_weights = {}
        self.g = g
        
        self.record = Record()

    def solve(self):
        start_time = time.time()
        tracemalloc.start()
        self.record.steps = 0
        self.record.node = 1
        #mem_before = Record.process_memory()

        g = self.g
        # (state, ares_pos, cost, path)
        # cost is only used for record
        initial_state, self.stone_weights = init_state(g)
        self.frontier.append( (initial_state, g.to_pos_2d(g.ares_pos), 0, '') )
        self.explored.clear()

        moves = Sokoban.moves()
    
        result = None

        while self.frontier:
            state, ares_pos, cost, path = self.frontier.pop(0)
            self.explored.add(state)
            # g.draw_state(state)

            for move in moves:
                new_state, move_cost, pushed = can_move(g, state, ares_pos, move, self.stone_weights)
                if new_state is None or new_state in self.explored or is_deadlock(g, new_state): #or new_state in self.frontier: #(doesn't matter)
                    continue
                if new_state in (f[0] for f in self.frontier):
                    continue
                path_dir =  Sokoban.move_to_char(move).upper() if pushed else Sokoban.move_to_char(move)
                if is_solved(new_state):
                    result = (cost + move_cost, path + path_dir)
                    break
                self.frontier.append((new_state, (ares_pos[0] + move[0], ares_pos[1] + move[1]), cost + move_cost, path + path_dir) )
                self.record.node += 1
            if result != None:
                break
        
        if result == None:
            return None
        
        self.record.time_ms = (time.time() - start_time) * 1000
        self.record.memory_mb =  tracemalloc.get_traced_memory()[1] / (1024**2) #(Record.process_memory() - mem_before) / 1024**2  
        tracemalloc.stop()
        self.record.weight = result[0] - len(result[1])
        self.record.steps = len(result[1])
        
        return result[1]
