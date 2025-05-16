"""config.py - Global variables in a sense"""
__version__ = '05/22/2025'
__author__ = 'Kayla Cao'

#constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (0, 100, 0)  # Dark green
TEXT_COLOR = (255, 255, 255)  # White
BUTTON_COLOR = (200, 200, 200)  # Light gray
BUTTON_HOVER_COLOR = (150, 150, 150)  # Darker gray
CARD_WIDTH = 100
CARD_HEIGHT = 145

# Game states
STATE_SETUP = 0
STATE_PREFLOP = 1
STATE_FLOP = 2
STATE_TURN = 3
STATE_RIVER = 4
STATE_SHOWDOWN = 5
STATE_GAME_OVER = 6 #lost the round
STATE_LOST = 7 #lost all money