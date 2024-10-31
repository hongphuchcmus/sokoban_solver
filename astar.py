import sokoban_console_refactored as skb
import time as time

class AStarSolver:
    def __init__(self, g: skb.Sokoban):
        self.g = g
        self.frontier = []
        self.fcosts = {}
        self.gcosts = {}
        self.parents = {}
        self.explored = set()
        self.transposition_table = {}

    def heuristic(state : skb.State):
        return 1

    def branch(self, g : skb.Sokoban, state: skb.State) -> tuple[int, list[skb.State]]:
        child_states = []
        for direction in skb.DIRECTIONS:
            
            ares_new_position = (state.ares_position[skb.Y] + direction[skb.Y], state.ares_position[skb.X] + direction[skb.X])
            if g.matrix_at(ares_new_position) == skb.WALL:
                continue
            
            new_stones = state.stone_positions.copy()
            weight = 1
            encountered_stone = False
            pushed = False

            # Check if ares can push any stones
            for stone_id in range(len(state.stone_positions)):
                stone_pos = state.stone_positions[stone_id]
                if stone_pos == ares_new_position:
                    encountered_stone = True
                    if g.can_push(state.ares_position, stone_pos, state):
                        new_stones[stone_id] = (stone_pos[skb.Y] + direction[skb.Y], stone_pos[skb.X] + direction[skb.X])
                        weight = g.get_stone_weight(stone_id)
                        pushed = True
                    break
            if encountered_stone and not pushed:
                continue

            child_state = skb.State(ares_new_position, new_stones)
            child_states.append((weight, child_state))

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
        g = self.g

        initial_state = self.initial_state(g)
        initial_state_hash = initial_state.get_hash()
        
        self.frontier = [initial_state_hash]
        self.fcosts = {initial_state_hash : self.heuristic(initial_state)}
        self.gcosts = {initial_state_hash : 0}
        self.transposition_table = {initial_state_hash : initial_state}
        self.explored.clear()
        self.parents = {initial_state_hash : None }

        found = False 
        # processed_count = 0
        goal_state_hash = ""

        while len(self.frontier) > 0:
            # Priority queue base on fcosts
            self.frontier.sort(key=lambda x: self.costs[x])
            
            current_hash = self.frontier.pop(0)
            print("Exploring state: ", current_hash)
            current = self.transposition_table[current_hash]
            
            g.draw_state(current)
            if g.is_solved(current):
                found = True
                goal_state_hash = current_hash
                print("Done!")
                break

            self.explored.add(current_hash)
            
            for weight, child in self.branch(g, current):
                child_hash = child.get_hash()

                if (child_hash not in self.frontier) and (child_hash not in self.explored):
                    
                    self.transposition_table[child_hash] = child
                    self.parents[child_hash] = current_hash
                    self.gcosts[child_hash] = self.gcosts[current_hash] + weight

                    self.frontier.append(child_hash)

                elif (child_hash in self.frontier) and (self.costs[child_hash] > self.gcosts[current_hash] + weight):
                    self.parents[child_hash] = current_hash
                    self.costs[child_hash] = self.costs[current_hash] + self.cost
        
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
        
        return "".join(path)
