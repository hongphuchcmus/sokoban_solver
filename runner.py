from sokoban import WALL, ARES, STONE, SPACE, SWITCH, ARES_ON_SWITCH, STONE_ON_SWITCH, Sokoban, Record, SokobanStateDrawingData
from solver_utils import can_move, is_deadlock, init_state, is_solved, WSTONES, WSTONES_ON_SWITCHES

class Runner:

    @staticmethod
    def run(g : Sokoban, path, delay = 0.0):
        initial_state, stone_weights_lookup = init_state(g)
        states = [ SokobanStateDrawingData(
            initial_state,
            Runner.stone_weights(initial_state, stone_weights_lookup), 0, 0, g)]
        ares_pos = g.to_pos_2d(g.ares_pos)
        
        for i in range(len(path)):
            move = Sokoban.char_to_move(path[i])
            new_state, move_cost, pushed = can_move(g, states[-1].state, ares_pos, move, stone_weights_lookup)
            if new_state is None:
                new_state = states[-1].state
            
            ares_pos = (ares_pos[0] + move[0], ares_pos[1] + move[1])

            added_weight = move_cost - 1 if pushed else 0 # Move cost was accounted for steps
            new_drawing_state = SokobanStateDrawingData(
                new_state,
                Runner.stone_weights(new_state, stone_weights_lookup),
                i+1, states[-1].weight + added_weight, g)
            
            states.append(new_drawing_state)
        
        for s in states:
            s.state = Runner.revert_state(s.state)

        return states

    # Stone weights in order of appearance
    @staticmethod
    def stone_weights(state, stone_weights_lookup):
        stone_weights = []
        for c in state:
            if c.lower() in stone_weights_lookup:
                stone_weights.append(stone_weights_lookup[c.lower()])
        return stone_weights
    
    # Revert state to use the default characters
    @staticmethod
    def revert_state(state):
        s = list(state)
        for i in range(len(s)):
            if s[i] in WSTONES + WSTONES_ON_SWITCHES:
                s[i] = STONE if s[i] in WSTONES else STONE_ON_SWITCH
        return "".join(s)
    
    @staticmethod
    def initial_state(g : Sokoban):
        initial_state, stone_weights_lookup = init_state(g)
        return SokobanStateDrawingData(
            Runner.revert_state(initial_state),
            Runner.stone_weights(initial_state, stone_weights_lookup), 0, 0, g)