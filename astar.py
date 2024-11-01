import sokoban_console_refactored as skb
import time as time
import sys 
import tracemalloc

class AStarSolver:
    def __init__(self, g: skb.Sokoban):
        self.g = g
        self.frontier = []
        self.hcosts = {}
        self.gcosts = {}
        self.parents = {}
        self.explored = set()
        self.transposition_table = {}
        
        self.record = skb.Record()

    def mahattan_distance(self, a, b):
        return abs(a[skb.Y] - b[skb.Y]) + abs(a[skb.X] - b[skb.X])

    def heuristic(self, g : skb.Sokoban, state : skb.State):
        h = 0
        switches = g.get_switches()
        for stone in state.stone_positions:
            smallest_distance = self.mahattan_distance(stone, switches[0])
            for i in range(1, len(switches)):
                distance = self.mahattan_distance(stone, switches[i])
                if distance < smallest_distance:
                    smallest_distance = distance 
            h += smallest_distance
        return h

    def branch(self, g : skb.Sokoban, state: skb.State):
        child_states = []
        for direction in skb.DIRECTIONS:
            
            ares_new_position = (state.ares_position[skb.Y] + direction[skb.Y], state.ares_position[skb.X] + direction[skb.X])
            if g.matrix_at(ares_new_position) == skb.WALL:
                continue
            
            new_stones = state.stone_positions.copy()
            g_cost = 1
            h_cost = 0
            encountered_stone = False
            pushed = False

            # Check if ares can push any stones
            for stone_id in range(len(state.stone_positions)):
                stone_pos = state.stone_positions[stone_id]
                if stone_pos == ares_new_position:
                    encountered_stone = True
                    if g.can_push(state.ares_position, stone_pos, state):
                        new_stones[stone_id] = (stone_pos[skb.Y] + direction[skb.Y], stone_pos[skb.X] + direction[skb.X])
                        g_cost = g.get_stone_weight(stone_id)
                        pushed = True
                    break
            if encountered_stone and not pushed:
                continue
            
            child_state = skb.State(ares_new_position, new_stones)
            self.record.node += 1

            h_cost = self.heuristic(g, child_state)

            child_states.append((g_cost, h_cost, child_state))
        return child_states

    def trace(self, g : skb.Sokoban, state_hash_path : list[skb.State]) -> str:
        path = []
        for i in range(len(state_hash_path)-1):
            current_state = self.transposition_table[state_hash_path[i]]
            next_state = self.transposition_table[state_hash_path[i+1]]

            ares_current_position = current_state.ares_position
            ares_next_position = next_state.ares_position

            move_direction = (ares_next_position[skb.Y] - ares_current_position[skb.Y], ares_next_position[skb.X] - ares_current_position[skb.X])
            
            is_pushing = False
            for stone_pos in current_state.stone_positions:
                if stone_pos == ares_next_position:
                    path.append(g.map_move_direction(move_direction).upper())
                    is_pushing = True
                    break
            if not is_pushing:
                path.append(g.map_move_direction(move_direction))
        return path
    
    def initial_state(self, g : skb.Sokoban) -> skb.State:
        return skb.State(g.initial_ares_position, g.initial_stone_positions)

    def solve(self) -> str:
        tracemalloc.start()
        start_time = time.time()
        self.record.weight = 0
        self.record.steps = 0
        self.record.node = 1

        g = self.g

        initial_state = self.initial_state(g)
        initial_state_hash = initial_state.get_hash()
        
        self.frontier = [initial_state_hash]
        self.hcosts = {initial_state_hash : self.heuristic(g, initial_state)}
        self.gcosts = {initial_state_hash : 0}
        self.transposition_table = {initial_state_hash : initial_state}
        self.explored.clear()
        self.parents = {initial_state_hash : None }

        found = False
        # processed_count = 0
        goal_state_hash = ""

        while len(self.frontier) > 0:
            # Priority queue base on fcosts
            self.frontier.sort(key=lambda x: (self.gcosts[x] + self.hcosts[x]))
            
            current_hash = self.frontier.pop(0)
            # print("Exploring state: ", current_hash)
            current = self.transposition_table[current_hash]
            
            # g.draw_state(current)
            if g.is_solved(current):
                found = True
                goal_state_hash = current_hash
                print("Done!")
                break

            self.explored.add(current_hash)
            for g_cost, h_cost, child in self.branch(g, current):
                child_hash = child.get_hash()
                if (child_hash not in self.frontier) and (child_hash not in self.explored):
                    
                    self.transposition_table[child_hash] = child
                    self.parents[child_hash] = current_hash
                    self.gcosts[child_hash] = self.gcosts[current_hash] + g_cost
                    self.hcosts[child_hash] = h_cost

                    self.frontier.append(child_hash)

                elif (child_hash in self.frontier) and (self.gcosts[child_hash] > self.gcosts[current_hash] + g_cost):
                    self.parents[child_hash] = current_hash
                    self.gcosts[child_hash] = self.gcosts[current_hash] + g_cost
        
        if not found:
            return ""

        # Tracing time!
        state_hash_path = []
        backtracer = goal_state_hash
        while backtracer:
            state_hash_path.append(backtracer)
            backtracer = self.parents[backtracer]
        state_hash_path.reverse()
        path = self.trace(g, state_hash_path)
        
        end_time = time.time()
        self.record.time_ms = (end_time - start_time) * 1000
        self.record.steps = len(path)
        self.record.weight = self.gcosts[goal_state_hash] - self.record.steps
        self.record.memory_mb = tracemalloc.get_traced_memory()[1] / 1000
        tracemalloc.stop()

        return "".join(path)
