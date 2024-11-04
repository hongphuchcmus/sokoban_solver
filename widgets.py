import pygame
from pygame_widgets.button import Button
from pygame_widgets.dropdown import Dropdown
from widgets_events import *
import os

# Color Constants
INACTIVE_COLOR = (212, 175, 55)
HOVER_COLOR = (212, 200, 75)
PRESSED_COLOR = (200, 100, 50)

INPUT_DIR = "input"

def get_widgets(screen : pygame.Surface, default_font : pygame.font.Font) -> dict:
	width, height = screen.get_size()
	algo_menu = Dropdown(screen, width * (1/3) - 50, 50, 100, 50, "Algorithm", ["BFS", "DFS", "UCS", "AStar"], False,
					font = default_font, fontSize = 20, borderRadius = 5,
					inactiveColour = INACTIVE_COLOR,
					hoverColour = HOVER_COLOR,
					pressedColour = PRESSED_COLOR,
					onRelease = lambda: pygame.event.post(pygame.event.Event(SELECT_ALGO_EVENT)))
	level_menu = Dropdown(screen, width * (2/3) - 50, 50, 100, 50, "Level", os.listdir(INPUT_DIR), False,
					font = default_font, fontSize = 20, borderRadius = 5,
					inactiveColour = INACTIVE_COLOR,
					hoverColour = HOVER_COLOR,
					pressedColour = PRESSED_COLOR,
					onRelease = lambda: pygame.event.post(pygame.event.Event(SELECT_MAP_EVENT)))
	run_button = Button(screen, width * (1/2) - 50, height * (1/2) + 150, 100, 50, False,
					text = "Run", font = default_font, radius = 5,
					inactiveColour = INACTIVE_COLOR,
					hoverColour = HOVER_COLOR,
					pressedColour = PRESSED_COLOR,
					onClick = lambda: pygame.event.post(pygame.event.Event(RUN_EVENT)))
	start_button = Button(screen, width * (1/5) - 50, height - 100, 100, 50, False,
					text = "Start", font = default_font, radius = 5,
					inactiveColour = INACTIVE_COLOR,
					hoverColour = HOVER_COLOR,
					pressedColour = PRESSED_COLOR,
					onClick = lambda: pygame.event.post(pygame.event.Event(START_EVENT)))
	pause_button = Button(screen, width * (2/5) - 50, height - 100, 100, 50, False,
					text = "Pause", font = default_font, radius = 5,
					inactiveColour = INACTIVE_COLOR,
					hoverColour = HOVER_COLOR,
					pressedColour = PRESSED_COLOR,
					onClick = lambda: pygame.event.post(pygame.event.Event(PAUSE_EVENT)))
	stop_button = Button(screen, width * (3/5) - 50, height - 100, 100, 50, False,
					text = "Stop", font = default_font, radius = 5,
					inactiveColour = INACTIVE_COLOR,
					hoverColour = HOVER_COLOR,
					pressedColour = PRESSED_COLOR,
					onClick = lambda: pygame.event.post(pygame.event.Event(STOP_EVENT)))
	back_button = Button(screen, width * (4/5) - 50, height - 100, 100, 50, False,
					text = "Back", font = default_font, radius = 5,
					inactiveColour = INACTIVE_COLOR,
					hoverColour = HOVER_COLOR,
					pressedColour = PRESSED_COLOR,
					onClick = lambda: pygame.event.post(pygame.event.Event(BACK_EVENT)))
	message_box = Button(screen, width * (1/2) - 100, height * (1/2) - 50, 200, 100, False,
					text = "Solving...", font = default_font, radius = 5,
					inactiveColour = INACTIVE_COLOR,
					hoverColour = HOVER_COLOR,
					pressedColour = PRESSED_COLOR)
	statistic_box = Button(screen, width * (1/2) - 100, 50, 200, 50, False,
					text = "Statistics", font = default_font, radius = 5,
					inactiveColour = INACTIVE_COLOR,
					hoverColour = HOVER_COLOR,
					pressedColour = PRESSED_COLOR)
	return {
		"algo_menu": algo_menu,
		"level_menu": level_menu,
		"run_button": run_button,
		"start_button": start_button,
		"pause_button": pause_button,
		"stop_button": stop_button,
		"back_button": back_button,
		"message_box": message_box,
		"statistic_box": statistic_box
	}
