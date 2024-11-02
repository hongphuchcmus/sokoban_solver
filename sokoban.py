import os
# import psutil
import time

ARES = "@"
WALL = "#"
SPACE = " "
STONE = "$"
SWITCH = "."
STONE_ON_SWITCH = "*"
ARES_ON_SWITCH = "+"



class Record:
    def __init__(self) -> None:
        self.steps = 0
        self.node = 0
        self.memory_mb = 0
        self.time_ms = 0
        self.weight = 0

    # @staticmethod
    # def process_memory():
    #     process = psutil.Process(os.getpid())
    #     mem_info = process.memory_info()
    #     return mem_info.rss

    # def data(self) -> str:
    #     return f"Steps: {self.steps}, Weight: {self.weight}, Node: {self.node}, Time (ms): {self.time_ms:6f}, Memory (MB): {self.memory_mb:6f}"


class Sokoban:
    def __init__(self, input_file):
        with open(input_file) as f:
            lines = f.read().splitlines()
            self.stone_weights = list(map(int, lines[0].split()))
            self.matrix = []
            for i in range(1, len(lines)):
                self.matrix.append(lines[i])
            self.rows = len(self.matrix)
            self.cols = len(self.matrix[0])
            self.matrix = "".join(self.matrix)
            self.ares_pos = self.matrix.index(ARES)
            # Unused spaces that cannot reachable
            self.outer_squares = self.init_outer_squares()
    
    def init_outer_squares(self):
        # A quick DFS to find the playable region of the map
        frontier = [self.to_pos_2d(self.ares_pos)]
        explored = set()
        while frontier:
            pos = frontier.pop()
            explored.add(pos)
            for move in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                new_pos = (pos[0] + move[0], pos[1] + move[1])
                if new_pos in explored:
                    continue
                if new_pos[0] < 0 or new_pos[0] >= self.rows or new_pos[1] < 0 or new_pos[1] >= self.cols:
                    continue
                if self.state_at(self.matrix, new_pos) == WALL:
                    continue
                frontier.append(new_pos)
        # outer squares will the space squares that aren't in the explored set
        outer_squares = set()
        for i in range(len(self.matrix)):
            pos = self.to_pos_2d(i)
            if self.matrix[i] == SPACE and pos not in explored:
                outer_squares.add(pos)
        return outer_squares

    def to_pos_2d(self, pos):
        return pos // self.cols, pos % self.cols
    
    def to_pos_1d(self, pos):
        return pos[0] * self.cols + pos[1]

    def state_at(self, state, pos):
        return state[pos[0] * self.cols + pos[1]]

    @staticmethod
    def char_to_move(char):
        char = char.lower()
        if char == "r":
            return (0, 1)
        elif char == "l":
            return (0, -1)
        elif char == "d":
            return (1, 0)
        elif char == "u":
            return (-1, 0)
        return (0, 0)

    @staticmethod
    def move_to_char(move):
        if move == (0, 1):
            return "r"
        elif move == (0, -1):
            return "l"
        elif move == (1, 0):
            return "d"
        elif move == (-1, 0):
            return "u"
        return ""
    
    @staticmethod
    def moves():
        return [(0, 1), (0, -1), (1, 0), (-1, 0)]
    
    @staticmethod
    def is_solved(state):
        return STONE not in state

    def draw_state(self, state):
        for i in range(len(state)):
            print(state[i], end="")
            if (i + 1) % self.cols == 0:
                print()
        print()
        