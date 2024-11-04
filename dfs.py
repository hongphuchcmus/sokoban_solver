from sokoban import Sokoban, Record
import time
import tracemalloc
from solver_utils import can_move, is_deadlock, init_state, is_solved, get_stones
from bfs import BFSSolver

class DFSSolver:
    def __init__(self, g : Sokoban) -> None:
        self.frontier = []
        self.explored = {None}
        self.stone_weights = {}
        self.g = g
        
        self.record = Record()

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
        # (state, ares_pos, cost, path)
        # cost is only used for record
        initial_state, self.stone_weights = init_state(g) 
        self.frontier.append((initial_state, g.to_pos_2d(g.ares_pos), 0, '') )
        self.explored.clear()
        
        # g.draw_state(g.matrix)
        moves = Sokoban.moves()

        result = None

        while self.frontier:
            if timeout != -1 and time.time() - start_time > timeout:
                print(f"Timeout! {timeout}s")
                self.timeout = True
                return None
            
            state, ares_pos, cost, path = self.frontier.pop()
            self.explored.add(state)
            
            # g.draw_state(state)

            for move in moves:
                new_state, move_cost, pushed = can_move(g, state, ares_pos, move, self.stone_weights)
                if new_state is None or new_state in self.explored or is_deadlock(g, new_state):
                    continue
                if new_state in (f[0] for f in self.frontier):
                    continue

                path_dir =  Sokoban.move_to_char(move).upper() if pushed else Sokoban.move_to_char(move)
                if is_solved(new_state):
                    result = (cost + move_cost, path + path_dir)
                    break
                self.frontier.append((new_state, (ares_pos[0] + move[0], ares_pos[1] + move[1]), cost + move_cost, path + path_dir) )
                
                if recorded:
                    self.record.node += 1
            
            if result != None:
                break
        
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
