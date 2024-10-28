# Prototype for sokoban solver
import time as time

ARES = "@"
WALL = "#"
SPACE = " "
STONE = "$"
SWITCH = "."
STONE_ON_SWITCH = "*"
ARES_ON_SWITCH = "+"

# Only use the fist time running the solver
def ares_position(puzzle_matrix):
    for i in range(len(puzzle_matrix)):
        for j in range(len(puzzle_matrix[i])):
            if puzzle_matrix[i][j] in [ARES, ARES_ON_SWITCH]:
                return (i, j)
    return (0, 0)
# Only use the fist time running the solver
def stone_positions(puzzle_matrix):
    stone_positions = []
    for i in range(len(puzzle_matrix)):
        for j in range(len(puzzle_matrix[i])):
            if puzzle_matrix[i][j] in [STONE, STONE_ON_SWITCH]:
                stone_positions.append((i, j))
    return stone_positions

def pushable_squares(puzzle_matrix, reachable_squares, stone_position, stone_positions):
    pushables = []
    for neighbor in neighbors(stone_position):
        if neighbor in reachable_squares and can_push(puzzle_matrix, stone_position, neighbor, stone_positions):
            pushables.append(neighbor)
    return pushables

def neighbors(position):
    x = position[0]
    y = position[1]
    return [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]

def max_cols(puzzle_matrix):
    cols = 0
    for i in range(len(puzzle_matrix)):
        if cols < len(puzzle_matrix[i]):
            cols = len(puzzle_matrix[i])
    return cols

def minreachable_square(puzzle_matrix, reachable_squares):
    min_square = reachable_squares[0]
    cols = max_cols()
    for i in range(1, len(reachable_squares)):
        if min_square[0] * cols + min_square[1] > reachable_squares[i][0] * cols + reachable_squares[i][1]:
            min_square = reachable_squares[i]
    return min_square

def reachable_squares(puzzle_matrix, ares_position, stone_positions):
    x = ares_position[0]
    y = ares_position[1]
    # A simple DFS to find reachable squares
    frontier = [(x, y)]
    explored = []
    while frontier:
        child = frontier.pop()
        explored.append(child)
        for neighbor in neighbors(child):
            x = neighbor[0]
            y = neighbor[1]
            if puzzle_matrix[x][y] != WALL \
                and (neighbor not in stone_positions) \
                    and (neighbor not in explored) \
                        and (neighbor not in frontier):
                frontier.append(neighbor)
    return explored

def branch(puzzle_matrix, state):
    child_states = []
    reachables = reachable_squares(puzzle_matrix, state[0], state[1])
    for i in range(len(state[1])):
        for pushable in pushable_squares(puzzle_matrix, reachables, state[1][i], state[1]):
            new_stones = list(state[1])
            new_stones[i] = push(puzzle_matrix, state[1][i], pushable)
            
            new_reachables = reachable_squares(puzzle_matrix, state[0], new_stones)

            child_states.append(get_state(new_reachables, new_stones))
    return child_states

def can_push(puzzle_matrix, stone_position, ares_position, stone_positions):
    x_translation = stone_position[0] - ares_position[0]
    y_translation = stone_position[1] - ares_position[1]
    new_position = (stone_position[0] + x_translation, stone_position[1] + y_translation)
    if puzzle_matrix[new_position[0]][new_position[1]] != WALL and (new_position not in stone_positions):
        return True
    return False

def push(puzzle_matrix, stone_position, ares_position):
    x_translation = stone_position[0] - ares_position[0]
    y_translation = stone_position[1] - ares_position[1]
    return (stone_position[0] + x_translation, stone_position[1] + y_translation)

def is_solved(puzzle_matrix, state):
    for stone_position in state[1]:
        if puzzle_matrix[stone_position[0]][stone_position[1]] not in SWITCH:
            return False
    return True

# Draw multiple states on one line
def draw_many_on_static_puzzle(static_puzzle_matrix, states):
    if len(states) == 0:
        return
    static_puzzle_matrix_clones = []
    for state in states:
        static_puzzle_matrix_clone = []
        for i in range(len(static_puzzle_matrix)):
            row = []
            for j in range(len(static_puzzle_matrix[i])):
                row.append(static_puzzle_matrix[i][j])
            static_puzzle_matrix_clone.append(row)
        if static_puzzle_matrix_clone[state[0][0]][state[0][1]] == SWITCH:
            static_puzzle_matrix_clone[state[0][0]][state[0][1]] = ARES_ON_SWITCH
        else:
            static_puzzle_matrix_clone[state[0][0]][state[0][1]] = ARES
        if state[1]:
            for stone in state[1]:
                if static_puzzle_matrix_clone[stone[0]][stone[1]] == SWITCH:
                    static_puzzle_matrix_clone[stone[0]][stone[1]] = STONE_ON_SWITCH
                else:
                    static_puzzle_matrix_clone[stone[0]][stone[1]] = STONE
        static_puzzle_matrix_clones.append(static_puzzle_matrix_clone)
    cols = max_cols(puzzle_matrix)
    for i in range(len(static_puzzle_matrix_clones[0])):
        for j in range(len(states)):
            for k in range(len(static_puzzle_matrix_clones[j][i])):
                print(static_puzzle_matrix_clones[j][i][k], end="")
            if k < cols - 1:
                for l in range(cols - k - 1):
                    print("-", end="")
            print(" "*8, end="")
        print()

def draw_puzzle(puzzle_matrix, highlight_positions = [], hightlighter = "█"):
    for i in range(len(puzzle_matrix)):
        for j in range(len(puzzle_matrix[i])):
            if (i, j) in highlight_positions:
                print(hightlighter, end="")
            else:
                print(puzzle_matrix[i][j], end="")
        print()

def draw_on_static_puzzle(static_puzzle_matrix, state, highlight_positions = [], hightlighter = "█"):
    static_puzzle_matrix_clone = []
    for i in range(len(static_puzzle_matrix)):
        row = []
        for j in range(len(static_puzzle_matrix[i])):
            row.append(static_puzzle_matrix[i][j])
        static_puzzle_matrix_clone.append(row)


    if static_puzzle_matrix_clone[state[0][0]][state[0][1]] == SWITCH:
        static_puzzle_matrix_clone[state[0][0]][state[0][1]] = ARES_ON_SWITCH
    else:
        static_puzzle_matrix_clone[state[0][0]][state[0][1]] = ARES
    
    for stone in state[1]:
        if static_puzzle_matrix_clone[stone[0]][stone[1]] == SWITCH:
            static_puzzle_matrix_clone[stone[0]][stone[1]] = STONE_ON_SWITCH
        else:
            static_puzzle_matrix_clone[stone[0]][stone[1]] = STONE

    draw_puzzle(static_puzzle_matrix_clone, highlight_positions, hightlighter)

def get_initial_state(puzzle_matrix):
    ares_pos = ares_position(puzzle_matrix)
    stones = stone_positions(puzzle_matrix)
    reachables = reachable_squares(puzzle_matrix, ares_pos, stones)
    min_reachable = minreachable_square(puzzle_matrix, reachables)
    return (min_reachable, tuple(stones)) 

def get_state(reachables, stone_positions):
    min_reachable = minreachable_square(puzzle_matrix, reachables)
    return (min_reachable, tuple(stone_positions)) 

def bfs(puzzle_matrix):
    initial_state = get_initial_state(puzzle_matrix)
    puzzle_matrix = get_static_puzzle_matrix(puzzle_matrix)
    initial_state_hash = str(hash(initial_state))
    tranposition_table = {initial_state_hash : initial_state}

    frontier = [initial_state_hash]
    explored = [initial_state_hash]
    parents = {initial_state_hash : None}
    
    found = False 
    processed_count = 0
    goal_state_hash = None

    while frontier:
        print("processed_count = ", processed_count)
        current_hash = frontier.pop(0)
        current = tranposition_table[current_hash]
        explored.append(current_hash)

        branching = []
        for child in branch(puzzle_matrix, current):
            child_hash = str(hash(child))
            if (child_hash not in explored) and (child_hash not in frontier):
                tranposition_table[child_hash] = child
                parents[child_hash] = current_hash
                if is_solved(puzzle_matrix, child):
                    found = True
                    goal_state_hash = child_hash
                    draw_on_static_puzzle(puzzle_matrix, child)
                    print("Done!")
                    break
                frontier.append(child_hash)
                branching.append(child)
        draw_many_on_static_puzzle(puzzle_matrix, branching)
        processed_count += 1
        time.sleep(0.001)
        if found:
            break
    
    if not found:
        print("No solution found")
        return
    
    path = []
    backtracer = goal_state_hash
    while backtracer:
        path.insert(0, backtracer)
        backtracer = parents[backtracer]
    for point in path:
        draw_on_static_puzzle(puzzle_matrix, tranposition_table[point])

def get_static_puzzle_matrix(puzzle_matrix):
    static_matrix = []

    for i in range(len(puzzle_matrix)):
        row = []
        for j in range(len(puzzle_matrix[i])):
            if puzzle_matrix[i][j] in [ARES, STONE]:
                row.append(SPACE)
            elif puzzle_matrix[i][j] in [ARES_ON_SWITCH, STONE_ON_SWITCH]:
                row.append(SWITCH)
            else:
                row.append(puzzle_matrix[i][j])
        static_matrix.append(row)
    return static_matrix

if __name__ == "__main__":
    puzzle_matrix = []
    with open("input.txt", "r") as file_in:
        lines = file_in.read().splitlines()
        for line in lines:
            puzzle_row = list(line)
            puzzle_matrix.append(puzzle_row)
    
    draw_puzzle(puzzle_matrix)
    bfs(puzzle_matrix)
    