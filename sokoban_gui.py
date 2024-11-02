import pygame as pg
import time
import os
from bfs import BFSSolver
from dfs import DFSSolver
from ucs import UCSSolver
from astar import AStarSolver
from sokoban import Sokoban
from runner import Runner

# Initialize Pygame
pg.init()

# Screen settings
TILE_SIZE = 30
ROWS, COLS = 20, 20
SCREEN_WIDTH, SCREEN_HEIGHT = COLS * TILE_SIZE, ROWS * TILE_SIZE  # Extra space for dropdown and buttons
FPS = 15
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("Sokoban Solver Visualization")

# Colors
COLOR_BUTTON = (100, 180, 195)
COLOR_BUTTON_TEXT = (255, 255, 255)

COLOR_MENU_BUTTON_INACTIVE = (100, 180, 195)
COLOR_MENU_BUTTON_ACTIVE = (120, 200, 255)
COLOR_MENU_ITEM_INACTIVE = (220, 220, 140)
COLOR_MENU_ITEM_ACTIVE = (245, 235, 160)
COLOR_MENU_ITEM_TEXT = (0, 0, 0)

COLOR_MESSAGE_BG = (220, 220, 140)
COLOR_MESSAGE_TEXT = (0, 0, 0)

# Font settings
button_font = pg.font.Font("./fonts/FreePixel.ttf", 16)

# Algorithm options
algorithms = ["BFS", "DFS", "A*", "UCS"]
selected_algorithm = None  # No selection by default
selected_test_case = None  # No test case selected

# Animation and state controls
START, PAUSE, STOP, BACK = 0, 1, 2, 3
animation_state = STOP
animation_step = 3 # Frames between states
state_index = 0
frame_index = 0

# A visual version of Sokoban state
class SokobanState:
    def __init__(self, steps, weight, state, g : Sokoban) -> None:
        self.cols = g.cols
        self.rows = g.rows
        self.outer_squares = g.outer_squares
        self.state = state
        self.steps = steps
        self.weight = weight

states = []

class MessageBox:
    def __init__(self, x, y, w, h, header, body, bg_color, text_color, font, life_time) -> None:
        self.rect = pg.Rect(x, y, w, h)
        self.header = header
        self.body = body
        self.bg_color = bg_color
        self.text_color = text_color
        self.font = font
        self.life_time = life_time
        self.updated_time = float("-inf")
    
    def draw(self, surf):
        pg.draw.rect(surf, self.bg_color, self.rect)
        header = self.font.render(self.header, 1, self.text_color)
        surf.blit(header, header.get_rect(center=(self.rect.centerx, self.rect.top + 15)))
        body = self.font.render(self.body, 1, self.text_color)
        surf.blit(body, body.get_rect(center=(self.rect.centerx, self.rect.top + 38)))
    
    def update(self, header, body):
        self.header = header
        self.body = body
        self.updated_time = pg.time.get_ticks() 
    
    def stop(self):
        self.updated_time = float("-inf")


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
    'start': Button(SCREEN_WIDTH * (1/5) - 50, SCREEN_HEIGHT - 80, 100, 40, "Start", COLOR_BUTTON, COLOR_BUTTON_TEXT, button_font),
    'pause': Button(SCREEN_WIDTH * (2/5) - 50, SCREEN_HEIGHT - 80, 100, 40, "Pause", COLOR_BUTTON, COLOR_BUTTON_TEXT, button_font),
    'stop': Button(SCREEN_WIDTH * (3/5) - 50, SCREEN_HEIGHT - 80, 100, 40, "Stop", COLOR_BUTTON, COLOR_BUTTON_TEXT, button_font),
    'back': Button(SCREEN_WIDTH * (4/5) - 50, SCREEN_HEIGHT - 80, 100, 40, "Back", COLOR_BUTTON, COLOR_BUTTON_TEXT, button_font),
}

class DropDown:
    def __init__(self, color_menu, color_option, x, y, w, h, text_color, item_text_color, font, main, options):
        self.color_menu = color_menu
        self.color_option = color_option
        self.rect = pg.Rect(x, y, w, h)
        self.text_color = text_color
        self.item_text_color = item_text_color
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
        msg = self.font.render(self.main, 1, self.text_color)
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
                msg = self.font.render(text, 1, self.item_text_color)
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
    [COLOR_MENU_BUTTON_INACTIVE, COLOR_MENU_BUTTON_ACTIVE],
    [COLOR_MENU_ITEM_INACTIVE, COLOR_MENU_ITEM_ACTIVE],
    dropdown_algorithm_x, dropdown_y, DROPDOWN_WIDTH, DROPDOWN_HEIGHT,
    COLOR_BUTTON_TEXT,
    COLOR_MENU_ITEM_TEXT,
    button_font, 
    "Select Algorithm", algorithms
)

dropdown_test_case = DropDown(
    [COLOR_MENU_BUTTON_INACTIVE, COLOR_MENU_BUTTON_ACTIVE],
    [COLOR_MENU_ITEM_INACTIVE, COLOR_MENU_ITEM_ACTIVE],
    dropdown_test_case_x, dropdown_y, DROPDOWN_WIDTH, DROPDOWN_HEIGHT, 
    COLOR_BUTTON_TEXT,
    COLOR_MENU_ITEM_TEXT,
    button_font, 
    "Select Test Case", [str(i) for i in range(1, 11)]
)

msg_boxes = {
    'statistics': MessageBox(SCREEN_WIDTH/2 - 200, 20, 400, 60, "", "", COLOR_MESSAGE_BG, COLOR_MESSAGE_TEXT, button_font, -1),
    'general': MessageBox(SCREEN_WIDTH/2 - 200, SCREEN_WIDTH/2 - 200, 400, 60, "", "", COLOR_MESSAGE_BG, COLOR_MESSAGE_TEXT, button_font, 2000)
}

# Background image
def draw_background():
    for i in range(ROWS):
        for j in range(COLS):
            bg = pg.image.load("textures/background.png").convert()
            bg = pg.transform.scale(bg, (TILE_SIZE, TILE_SIZE))
            screen.blit(bg, (i * TILE_SIZE, j * TILE_SIZE))

# Draw matrix function
def draw_sokoban_state(screen : pg.surface, s : SokobanState):
    center_offset = (ROWS/2-s.rows/2, COLS/2-s.cols/2)
    for i in range(s.rows):
        for j in range(s.cols):
            x, y = (j + center_offset[1]) * TILE_SIZE , (i + center_offset[0]) * TILE_SIZE
            tile = s.state[i][j]

            # Draw a different texture for the inner region
            if (i, j) not in s.outer_squares:
                img = pg.image.load("textures/inner_floor.png").convert()
                img = pg.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                screen.blit(img, (x, y))
            if tile == "#":
                img = pg.image.load("textures/wall.png").convert()
                img = pg.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                screen.blit(img, (x, y))
            if tile in ".*+":
                img = pg.image.load("textures/switch.png").convert()
                img = pg.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                screen.blit(img, (x, y))
            if tile in "@+":
                img = pg.image.load("textures/link.png").convert_alpha()
                img = pg.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                screen.blit(img, (x, y))
            if tile in "$*":
                img = pg.image.load("textures/stone.png").convert_alpha()
                img = pg.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                screen.blit(img, (x, y))
            
# Main loop with dropdown integration
running = True
show_dropdowns = True
clock = pg.time.Clock()

while running:
    draw_background()
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
            dropdown_algorithm.main = f"Algorithm: {selected_algorithm}"

        # Set test case based on selection
        if selected_test_case_index >= 0:
            selected_test_case = dropdown_test_case.options[selected_test_case_index]
            dropdown_test_case.main = f"Test case: {selected_test_case}"

        # Check if both selections are made
        if selected_algorithm and selected_test_case:

            # Load selected test map
            map_file = f"Tests/{selected_test_case}.txt"
            g = Sokoban(map_file)
            
            solver = None
            # Initialize the solver based on selected algorithm
            if selected_algorithm == "BFS":
                solver = BFSSolver(g)
            elif selected_algorithm == "DFS":
                solver = DFSSolver(g)
            elif selected_algorithm == "UCS":
                solver = UCSSolver(g)
            elif selected_algorithm == "A*":
                solver = AStarSolver(g)
            else:
                solver = BFSSolver(g)
            
            path = solver.solve(recorded=False)
            # Get all the states throughout the path
            if path is not None:
                states = []
                weights_and_states = Runner.run(g, path)
                for i in range(len(weights_and_states)):
                    weight, state = weights_and_states[i]
                    states.append(SokobanState(i, weight, state, g))
                show_dropdowns = False
                msg_boxes['general'].stop()
                animation_state = STOP
            else:
                msg_boxes['general'].update("No solution found", "Please select another algorithm or test case")
                show_dropdowns = True
                selected_algorithm = None
                selected_test_case = None
                dropdown_algorithm.main = "Select Algorithm"
                dropdown_test_case.main = "Select Test Case"
    else:
        # Draw the control buttons for animation
        for button in buttons.values():
            button.draw(screen)

        # Check for button interactions
        mouse_pos = pg.mouse.get_pos()
        mouse_pressed = pg.mouse.get_pressed()[0]
        if buttons['start'].is_clicked(mouse_pos, mouse_pressed) and path:
            animation_state = START
            frame_index = 0
            state_index = 0
        elif buttons['pause'].is_clicked(mouse_pos, mouse_pressed):
            animation_state = PAUSE
        elif buttons['stop'].is_clicked(mouse_pos, mouse_pressed):
            animation_state = STOP
            state_index = 0
        elif buttons['back'].is_clicked(mouse_pos, mouse_pressed):
            animation_state = BACK

        header = f"Algorithm: {selected_algorithm} | Test Case: {selected_test_case}"

        # Handle animation
        if animation_state == START and state_index < len(states):
            if state_index == len(states) - 1:
                draw_sokoban_state(screen, states[state_index])
                msg_boxes['statistics'].update("FINISHED! " + header, f"Steps: {states[state_index].steps} | Weight pushed: {states[state_index].weight}")
            else:
                # Clamp the animation
                frame_index += 1
                if frame_index % animation_step != 0:
                    draw_sokoban_state(screen, states[state_index])
                else:
                    state_index += 1
                    draw_sokoban_state(screen, states[state_index])
                msg_boxes['statistics'].update("RUNNING..." + header, f"Steps: {states[state_index].steps} | Weight pushed: {states[state_index].weight}")
        elif animation_state == STOP:
            state_index = 0
            frame_index = 0
            draw_sokoban_state(screen, states[state_index])
            msg_boxes['statistics'].update("STOPPED. " + header, "Click \"Start\" to visualize the solution")
        elif animation_state == PAUSE and state_index < len(states):
            draw_sokoban_state(screen, states[state_index])
            msg_boxes['statistics'].update("PAUSED. " + header, f"Steps: {states[state_index].steps} | Weight pushed: {states[state_index].weight}")
        # If animation_state == BACK, then return to the dropdowns for users
        # to select another algorithm and test case
        elif animation_state == BACK:
            show_dropdowns = True
            selected_algorithm = None
            selected_test_case = None
            dropdown_algorithm.main = "Select Algorithm"
            dropdown_test_case.main = "Select Test Case"
            animation_state = START

        msg_boxes['statistics'].draw(screen)
    
    # Draw message boxes
    for msg_box in msg_boxes.values():
        if msg_box.life_time > 0 and pg.time.get_ticks() - msg_box.updated_time < msg_box.life_time:
            msg_box.draw(screen)

    # Draw dropdowns if visible
    if show_dropdowns:
        dropdown_algorithm.draw(screen)
        dropdown_test_case.draw(screen)

    pg.display.flip()

    clock.tick(FPS)

pg.quit()
