from sokoban import WALL, ARES, STONE, SPACE, SWITCH, ARES_ON_SWITCH, STONE_ON_SWITCH, Sokoban

WSTONES = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
WSTONES_ON_SWITCHES = "abcdefghijklmnopqrstuvwxyz"

def get_stones(g : Sokoban, state):
    stones = []
    stone_markers = WSTONES + WSTONES_ON_SWITCHES
    for i in range(len(state)):
        if state[i] in stone_markers:
            stones.append(g.to_pos_2d(i))
    return stones

def stones_and_switches(g : Sokoban, state):
    stones = []; switches = []
    for i in range(len(state)):
        if state[i] in WSTONES + WSTONES_ON_SWITCHES:
            stones.append(g.to_pos_2d(i))
        elif state[i] in (SWITCH, ARES_ON_SWITCH):
            switches.append(g.to_pos_2d(i))
    return stones, switches

def is_deadlock(g : Sokoban , state):
        stones = get_stones(g, state)
        # Conner deadlock
        # ## ## $# #$
        # #$ $# ## ##
        if "conner deadlock":
            for stone in stones:
                if g.state_at(state, stone) in WSTONES_ON_SWITCHES:
                    continue
                #  #
                # #$
                if g.state_at(state, (stone[0] - 1, stone[1])) == WALL and g.state_at(state, (stone[0], stone[1] - 1)) == WALL:
                    return True
                # #
                # $#
                if g.state_at(state, (stone[0], stone[1] + 1)) == WALL and g.state_at(state, (stone[0] - 1, stone[1])) == WALL:
                    return True
                # $#
                # # 
                if g.state_at(state, (stone[0] + 1, stone[1])) == WALL and g.state_at(state, (stone[0], stone[1] + 1)) == WALL:
                    return True
                # #$
                #  #
                if g.state_at(state, (stone[0], stone[1] - 1)) == WALL and g.state_at(state, (stone[0] + 1, stone[1])) == WALL:
                    return True
        if "multi-boxes deadlock":
            #      2 boxes      |   3 boxes   | 4 boxes
            # $$ ## #$ $# $# #$ | $$ $# #$ $$ | $$     
            # ## $$ #$ $# #$ $# | $# $$ $$ #$ | $$     
            multiboxes_deadlock_patterns = {"$$##", "##$$", "#$#$", "$#$#", "$##$", "#$$#",
                                            "$$$#", "$#$$", "#$$$", "$$#$", "$$$$"}
            check_state = list(state)
            for i in range(len(check_state)):
                if check_state[i] in WSTONES_ON_SWITCHES:
                    check_state[i] = STONE_ON_SWITCH
                elif check_state[i] in WSTONES:
                    check_state[i] = STONE
            check_state = "".join(check_state)
            for stone in stones:
                for x in range(-1, 1):
                    for y in range(-1, 1):
                        pattern = []
                        pattern.append(g.state_at(check_state, (stone[0] + x, stone[1]+y)))
                        pattern.append(g.state_at(check_state, (stone[0] + x, stone[1]+y+1)))
                        pattern.append(g.state_at(check_state, (stone[0] + x+1, stone[1]+y)))
                        pattern.append(g.state_at(check_state, (stone[0] + x+1, stone[1]+y+1)))
                        pattern = "".join(pattern)
                        if STONE in pattern and pattern in multiboxes_deadlock_patterns:
                            return True
        return False

# Return (newstate, movecost, pushed)
def can_move(g : Sokoban, state, ares_pos, move, stone_weights):
    new_state = list(state)
    move_cost = 0
    pushed = False
    
    ares_pos_1d = g.to_pos_1d(ares_pos)
    new_ares_pos_1d = g.to_pos_1d((ares_pos[0] + move[0], ares_pos[1] + move[1]))
    new_stone_position_1d = g.to_pos_1d((ares_pos[0] + 2 * move[0], ares_pos[1] + 2 * move[1]))

    # print(g.to_pos_2d(new_ares_pos_1d))
    if state[new_ares_pos_1d] == WALL:
        return None, move_cost, pushed
    elif state[new_ares_pos_1d] in [SPACE, SWITCH]:
        new_state[ares_pos_1d] = SWITCH if state[ares_pos_1d] == ARES_ON_SWITCH else SPACE
        new_state[new_ares_pos_1d] = ARES_ON_SWITCH if state[new_ares_pos_1d] == SWITCH else ARES
        move_cost = 1
    elif state[new_ares_pos_1d] in WSTONES + WSTONES_ON_SWITCHES:
        if state[new_stone_position_1d] in WSTONES + WSTONES_ON_SWITCHES + WALL:
            return None, move_cost, pushed
        elif state[new_stone_position_1d] in SPACE + SWITCH:
            new_state[ares_pos_1d] = SWITCH if state[ares_pos_1d] == ARES_ON_SWITCH else SPACE
            new_state[new_ares_pos_1d] = ARES_ON_SWITCH if state[new_ares_pos_1d] in WSTONES_ON_SWITCHES else ARES
            new_state[new_stone_position_1d] = state[new_ares_pos_1d].lower() if state[new_stone_position_1d] == SWITCH else state[new_ares_pos_1d].upper()
            move_cost = 1 + stone_weights[state[new_ares_pos_1d].lower()]
            pushed = True
    
    return "".join(new_state), move_cost, pushed

def is_solved(state):
    for c in state:
        if c in WSTONES:
            return False
    return True

def init_state(g : Sokoban):
    stone_weights = {}
    state = list(g.matrix)
    stone_index = 0
    for i in range(len(state)):
        if state[i] in (STONE, STONE_ON_SWITCH):
            stone_weights[WSTONES_ON_SWITCHES[stone_index]] = g.stone_weights[stone_index]
            if state[i] in STONE:
                state[i] = WSTONES[stone_index]
                stone_index += 1
            else:
                state[i] = WSTONES_ON_SWITCHES[stone_index]
                stone_index += 1
    return "".join(state), stone_weights
