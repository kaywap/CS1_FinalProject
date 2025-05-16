"""button.py"""
__version__ = '05/22/2025'
__author__ = 'Kayla Cao'

import pygame

class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, text, font,
                 idle_color=(200, 200, 200),
                 hover_color=(150, 150, 150),
                 text_color=(0, 0, 0)):
        """Initialization"""
        super().__init__()

        self.image = pygame.Surface((width, height))
        self.rect = self.image.get_rect(topleft=(x, y))

        self.text = text
        self.font = font
        self.idle_color = idle_color
        self.hover_color = hover_color
        self.text_color = text_color

        self.render()

    def render(self, hover=False):
        """renders the button"""
        if hover:
            color = self.hover_color
        else:
            color = self.idle_color
        self.image.fill(color)

        text_surface = self.font.render(self.text, True, (0, 0, 0))  # Black text
        text_rect = text_surface.get_rect(center=(self.rect.width // 2, self.rect.height // 2))

        # Blit text onto the button surface
        self.image.blit(text_surface, text_rect)

    def is_hovered(self, mouse_pos):
        """returns the mouse location if it hovers over the button"""
        return self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        """draws the button"""
        screen.blit(self.image, self.rect)