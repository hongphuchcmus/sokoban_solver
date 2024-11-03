from sokoban import WALL, ARES, STONE, SPACE, SWITCH, ARES_ON_SWITCH, STONE_ON_SWITCH, Sokoban, Record
from solver_utils import can_move, is_deadlock, init_state, is_solved, revert_state

class Runner:

    @staticmethod
    def run(g : Sokoban, path, delay = 0.0):
        initial_state, stone_weights = init_state(g)
        # (weight,state)
        states = [[0, initial_state]]
        ares_pos = g.to_pos_2d(g.ares_pos)
        
        for move_char in path:
            move = Sokoban.char_to_move(move_char)
            new_state, move_cost, pushed = can_move(g, states[-1][1], ares_pos, move, stone_weights)
            if new_state is None:
                break 
            
            ares_pos = (ares_pos[0] + move[0], ares_pos[1] + move[1])

            added_weight = move_cost - 1 if pushed else 0 # Move cost was accounted for steps
            states.append([states[-1][0] + added_weight, new_state])
        
        # Hide the weighting characters
        # for i in range(len(states)):
        #     # print(states[i][1])
        #     states[i][1] = revert_state(states[i][1])
        
        # return states

        # Hide the weighting characters
        for i in range(len(states)):
            # print(states[i][1])
            states[i][1] = revert_state(states[i][1])
            states[i][1] = Runner.state_string_to_string_list(g, states[i][1])
        
        return states

    @staticmethod
    def state_string_to_string_list(g : Sokoban, state) -> list[str]:
        state_str_list = []
        for i in range(g.rows):
            row = ""
            for j in range(g.cols):
                row += state[g.to_pos_1d((i, j))]
            state_str_list.append(row)
        return state_str_list