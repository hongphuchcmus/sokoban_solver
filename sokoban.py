import os
import psutil
import time
from colorama import Fore, Back, Style

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

    @staticmethod
    def process_memory(global_process : psutil.Process):
        mem_info = global_process.memory_info()
        return mem_info.rss

    def data(self) -> str:
        return f"Steps: {self.steps}, Weight: {self.weight}, Node: {self.node}, Time (ms): {self.time_ms:6f}, Memory (MB): {self.memory_mb:6f}"

class Sokoban:
    def __init__(self, input_file, matrix=None, cols=None, rows=None, stone_weights=None) -> None:
        m = ""
        r, c = 0, 0
        w = []
        ares = 0
        
        # You can either pass in the matrix or the input file
        if matrix is not None and cols is not None and rows is not None:
            m = matrix
            r = rows
            c = cols
            w = stone_weights
        else:
            with open(input_file) as f:
                lines = f.read().splitlines()
                w = list(map(int, lines[0].split()))
                m = []
                for i in range(1, len(lines)):
                    m.append(lines[i])
                r = len(m)
                c = len(m[0])
                m = "".join(m)
        for i in range(len(m)):
            if m[i] in (ARES, ARES_ON_SWITCH):
                ares = i
        switches = []
        for i in range(len(m)):
            if m[i] in (SWITCH, STONE_ON_SWITCH):
                switches.append(i)
        self.matrix = m
        self.rows = r
        self.cols = c
        self.stone_weights = w
        self.ares_pos = ares
        self.switch_pos = switches
        self.outer_squares = self.init_outer_squares()

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
    
    def draw_state(self, state, hightlights=[]):
        for i in range(len(state)):
            if i in hightlights:
                print(Back.WHITE + Fore.CYAN + state[i], end="")
                print(Style.RESET_ALL, end="")
            else:
                print(state[i], end="")
            if (i + 1) % self.cols == 0:
                print()
    
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
        return outer_squares # 2d pos

class SokobanStateDrawingData:
    def __init__(self, state, stone_weights, steps, weight, g : Sokoban) -> None:
        self.rows = g.rows
        self.cols = g.cols
        self.steps = steps
        self.weight = weight
        self.state = state # string list format
        self.stone_weights = stone_weights # stone weights in order of appearance
        self.outer_squares = g.outer_squares
    
    def state_at(self, pos):
        return self.state[pos[0] * self.cols + pos[1]]