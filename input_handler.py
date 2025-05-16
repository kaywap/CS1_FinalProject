"""input_handler.py - makes taking input and blitting to screen easier"""
__version__ = '05/22/2025'
__author__ = 'Kayla Cao'

import pygame
from config import *

class InputHandler:
    @staticmethod #no self variables
    def get_numeric_input(screen, message, x, y, min_value=0, max_value=None):
        """gets a numeric input from the user"""
        input_text = ''
        clock = pygame.time.Clock()

        # Create a background surface
        input_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        input_surface.fill(BACKGROUND_COLOR)

        error_message = ""

        while True:
            clock.tick(10)  # Limit frame rate
            for event in pygame.event.get():
                if event.type == pygame.QUIT or \
                        (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    return None

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and input_text:
                        try:
                            value = int(input_text)

                            # Validate input
                            if value < min_value:
                                error_message = f"Must be at least {min_value}"
                                input_text = ''
                                continue

                            if max_value is not None and value > max_value:
                                error_message = f"Cannot exceed {max_value}"
                                input_text = ''
                                continue

                            return value

                        except ValueError:
                            # Invalid input, try again
                            input_text = ''
                            error_message = "Invalid input"

                    elif event.key == pygame.K_BACKSPACE and input_text:
                        input_text = input_text[:-1]

                    elif event.unicode.isdigit():
                        input_text += event.unicode

            # Draw background
            screen.blit(input_surface, (0, 0))

            # Draw main text
            font = pygame.font.Font(None, 50)
            text = font.render(f'{message} {input_text}', True, (255, 255, 255))
            text_rect = text.get_rect(center=(x, y))
            screen.blit(text, text_rect)

            # Draw error message if any
            if error_message:
                error_font = pygame.font.Font(None, 36)
                error_text = error_font.render(error_message, True, (255, 0, 0))
                error_rect = error_text.get_rect(center=(x, y + 50))
                screen.blit(error_text, error_rect)

            pygame.display.flip()