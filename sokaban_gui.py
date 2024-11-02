import pygame as pg
import time
import os
from bfs import BFSSolver
from dfs import DFSSolver
from ucs import UCSSolver
from astar import AStarSolver
import sokoban as skb
from runner import Runner

# Initialize Pygame
pg.init()

# Screen settings
TILE_SIZE = 30
ROWS, COLS = 20, 20
SCREEN_WIDTH, SCREEN_HEIGHT = COLS * TILE_SIZE, ROWS * TILE_SIZE + 50  # Extra space for dropdown and buttons
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("Sokoban Solver Visualization")

# Colors
COLOR_WALL = (100, 100, 100)
COLOR_SPACE = (255, 255, 255)
COLOR_PLAYER = (0, 0, 255)
COLOR_STONE = (139, 69, 19)
COLOR_SWITCH = (255, 215, 0)
COLOR_STONE_ON_SWITCH = (255, 140, 0)
COLOR_PLAYER_ON_SWITCH = (30, 144, 255)
COLOR_BUTTON = (70, 130, 180)
COLOR_BUTTON_TEXT = (255, 255, 255)

# Font settings
button_font = pg.font.Font(None, 30)

# Algorithm options
algorithms = ["BFS", "DFS", "A*", "UCS"]
selected_algorithm = None  # No selection by default
selected_test_case = None  # No test case selected

# Animation and state controls
START, PAUSE, STOP = 0, 1, 2
BACK = 3
animation_state = STOP
frame_index = 0

# Solver and path
solver_instance = None
path = []
matrices = []

# Button class
class Button:
    def __init__(self, x, y, width, height, text, color, text_color, font):
        self.rect = pg.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = font

    def draw(self, surface):
        pg.draw.rect(surface, self.color, self.rect)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.rect.collidepoint(mouse_pos) and mouse_pressed

# Initialize control buttons
buttons = {
    'start': Button(50, SCREEN_HEIGHT - 80, 100, 40, "Start", COLOR_BUTTON, COLOR_BUTTON_TEXT, button_font),
    'pause': Button(200, SCREEN_HEIGHT - 80, 100, 40, "Pause", COLOR_BUTTON, COLOR_BUTTON_TEXT, button_font),
    'stop': Button(350, SCREEN_HEIGHT - 80, 100, 40, "Stop", COLOR_BUTTON, COLOR_BUTTON_TEXT, button_font),
    'back': Button(500, SCREEN_HEIGHT - 80, 100, 40, "Back", COLOR_BUTTON, COLOR_BUTTON_TEXT, button_font),
    'finish': Button(650, SCREEN_HEIGHT - 80, 100, 40, "Finish", COLOR_BUTTON, COLOR_BUTTON_TEXT, button_font),
}

class DropDown:
    def __init__(self, color_menu, color_option, x, y, w, h, font, main, options):
        self.color_menu = color_menu
        self.color_option = color_option
        self.rect = pg.Rect(x, y, w, h)
        self.font = font
        self.main = main
        self.options = options
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1
        self.direction_up = False  # New attribute to track dropdown direction

    def draw(self, surf):
        # Draw main menu button
        pg.draw.rect(surf, self.color_menu[self.menu_active], self.rect, 0)
        msg = self.font.render(self.main, 1, (0, 0, 0))
        surf.blit(msg, msg.get_rect(center=self.rect.center))

        # Check available space to determine dropdown direction
        screen_height = surf.get_height()
        option_height = len(self.options) * self.rect.height
        self.direction_up = self.rect.bottom + option_height > screen_height

        # Draw options
        if self.draw_menu:
            for i, text in enumerate(self.options):
                option_rect = self.rect.copy()
                # Position options either above or below the main button based on space
                option_rect.y -= (i + 1) * self.rect.height if self.direction_up else (i + 1) * -self.rect.height
                pg.draw.rect(surf, self.color_option[1 if i == self.active_option else 0], option_rect, 0)
                msg = self.font.render(text, 1, (0, 0, 0))
                surf.blit(msg, msg.get_rect(center=option_rect.center))

    def update(self, event_list):
        mpos = pg.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)
        
        # Check active option index
        self.active_option = -1
        for i in range(len(self.options)):
            option_rect = self.rect.copy()
            option_rect.y -= (i + 1) * self.rect.height if self.direction_up else (i + 1) * -self.rect.height
            if option_rect.collidepoint(mpos):
                self.active_option = i
                break

        # Hide menu if not hovered
        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        # Handle clicks
        for event in event_list:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                elif self.draw_menu and self.active_option >= 0:
                    self.draw_menu = False
                    return self.active_option
        return -1

# Initialize dropdowns
COLOR_INACTIVE = (100, 80, 255)
COLOR_ACTIVE = (100, 200, 255)
COLOR_LIST_INACTIVE = (255, 100, 100)
COLOR_LIST_ACTIVE = (255, 150, 150)

# Centered dropdown dimensions and positioning
DROPDOWN_WIDTH, DROPDOWN_HEIGHT = 200, 50
PADDING_BETWEEN = 20  # Space between the two dropdowns

# Calculate x-coordinates for centered positioning
dropdown_algorithm_x = (SCREEN_WIDTH - 2 * DROPDOWN_WIDTH - PADDING_BETWEEN) // 2
dropdown_test_case_x = dropdown_algorithm_x + DROPDOWN_WIDTH + PADDING_BETWEEN
#dropdown_y = (SCREEN_HEIGHT - 350) // 2  # Vertical center above control buttons
dropdown_y = 10
# Initialize dropdowns with new centered positions
dropdown_algorithm = DropDown(
    [COLOR_INACTIVE, COLOR_ACTIVE],
    [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
    dropdown_algorithm_x, dropdown_y, DROPDOWN_WIDTH, DROPDOWN_HEIGHT, 
    pg.font.SysFont(None, 30), 
    "Select Algorithm", algorithms
)

dropdown_test_case = DropDown(
    [COLOR_INACTIVE, COLOR_ACTIVE],
    [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
    dropdown_test_case_x, dropdown_y, DROPDOWN_WIDTH, DROPDOWN_HEIGHT, 
    pg.font.SysFont(None, 30), 
    "Select Test Case", [str(i) for i in range(1, 11)]
)

# Draw matrix function
def draw_matrix(matrix):
    rows = len(matrix)
    cols = len(matrix[0])
    offset = (ROWS/2-rows/2, COLS/2-cols/2)
    for row in range(len(matrix)):
        for col in range(len(matrix[row])):
            x, y = (col+ offset[1]) * TILE_SIZE , (row + offset[0]) * TILE_SIZE
            tile = matrix[row][col]
            if tile == "#":
                img = pg.image.load("textures/wall.png").convert_alpha()
                img = pg.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                screen.blit(img, (x, y))
            elif tile == ".":
                img = pg.image.load("textures/switch.png").convert()
                img = pg.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                screen.blit(img, (x, y))
            elif tile in "@+":
                img = pg.image.load("textures/ares.png").convert_alpha()
                img = pg.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                screen.blit(img, (x, y))
            elif tile in "$*":
                img = pg.image.load("textures/stone.png").convert_alpha()
                img = pg.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                screen.blit(img, (x, y))
            # color_map = {"#": COLOR_WALL, " ": COLOR_SPACE, "@": COLOR_PLAYER,
            #              "$": COLOR_STONE, ".": COLOR_SWITCH, "*": COLOR_STONE_ON_SWITCH, "+": COLOR_PLAYER_ON_SWITCH}
            # pg.draw.rect(screen, color_map.get(tile, COLOR_SPACE), (x, y, TILE_SIZE, TILE_SIZE))

# Load test map based on selection
def load_test_map(test_case): 
    return f"Tests/{test_case}.txt"

# Main loop with dropdown integration
running = True
show_dropdowns = True

while running:
    screen.fill(COLOR_SPACE)
    event_list = pg.event.get()

    # Process events
    for event in event_list:
        if event.type == pg.QUIT:
            running = False

    # Handle dropdowns and selection of algorithm and test case
    if show_dropdowns:
        selected_algorithm_index = dropdown_algorithm.update(event_list)
        selected_test_case_index = dropdown_test_case.update(event_list)

        # Set algorithm based on selection
        if selected_algorithm_index >= 0:
            selected_algorithm = dropdown_algorithm.options[selected_algorithm_index]
            dropdown_algorithm.main = selected_algorithm

        # Set test case based on selection
        if selected_test_case_index >= 0:
            selected_test_case = dropdown_test_case.options[selected_test_case_index]
            dropdown_test_case.main = f"Test {selected_test_case}"

        # Check if both selections are made
        if selected_algorithm and selected_test_case:
            show_dropdowns = False  # Hide dropdowns

            # Load selected test map
            map_file = load_test_map(selected_test_case)
            g = skb.Sokoban(map_file)
            
            # Initialize the solver based on selected algorithm
            if selected_algorithm == "BFS":
                solver_instance = BFSSolver(g)
            elif selected_algorithm == "DFS":
                solver_instance = DFSSolver(g)
            elif selected_algorithm == "UCS":
                solver_instance = UCSSolver(g)
            elif selected_algorithm == "A*":
                solver_instance = AStarSolver(g)
            path = solver_instance.solve()
            matrices = Runner.run(g,path)
    else:
        # Draw the control buttons after selections are made
        for button in buttons.values():
            button.draw(screen)

        # Check for button interactions
        mouse_pos = pg.mouse.get_pos()
        mouse_pressed = pg.mouse.get_pressed()[0]
        if buttons['start'].is_clicked(mouse_pos, mouse_pressed) and path:
            animation_state = START
        elif buttons['pause'].is_clicked(mouse_pos, mouse_pressed):
            animation_state = PAUSE
        elif buttons['stop'].is_clicked(mouse_pos, mouse_pressed):
            animation_state = STOP
            frame_index = 0
        elif buttons['back'].is_clicked(mouse_pos, mouse_pressed):
            animation_state = BACK
        #when Finish button is cliked, the animation will finish, the Pygame will close
        # elif buttons['finish'].is_clicked(mouse_pos, mouse_pressed):
        #     animation_state = STOP
        #     frame_index = len(matrices) - 1 # Finish animation


        # Handle animation
        if animation_state == START and frame_index < len(matrices):
            draw_matrix(matrices[frame_index])
            frame_index += 1
            if frame_index == len(matrices):
                frame_index = len(matrices) - 1
            time.sleep(0.1)
        elif animation_state == STOP:
            frame_index = 0
            draw_matrix(matrices[0])
        elif animation_state == PAUSE and frame_index < len(matrices):
            draw_matrix(matrices[frame_index])
        #IF animation_state == BACK, then return to the dropdowns for users to select another algorithm and test case
        elif animation_state == BACK:
            show_dropdowns = True
            selected_algorithm = None
            selected_test_case = None
            solver_instance = None
            path = []
            matrices = []
            animation_state = START

    # Draw dropdowns if visible
    if show_dropdowns:
        dropdown_algorithm.draw(screen)
        dropdown_test_case.draw(screen)

    pg.display.flip()

pg.quit()
