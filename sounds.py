"""Sound manager that manages all the sounds you hear in the game. """
__version__ = '05/22/2025'
__author__ = 'Kayla Cao'

import pygame

class SoundManager:
    """Manages your sounds"""
    def __init__(self):
        """initialization"""
        # Initialize pygame mixer
        pygame.mixer.init()

        # Load sounds (make sure to have these sound files in a 'sounds' folder)
        try:
            self.game_finished_sound = pygame.mixer.Sound("sounds/game_finished.wav")
            self.poker_chip_sound = pygame.mixer.Sound("sounds/poker_chip.wav")

            # Background music
            self.bg_music = pygame.mixer.Sound('sounds/bg_music.wav')

        except Exception as e:
            print(f"Error loading sounds: {e}")

    def play_game_finished(self):
        """plays woo! sound"""
        self.game_finished_sound.play()

    def play_poker_chip(self):
        """plays chips sound"""
        self.poker_chip_sound.play()
        self.poker_chip_sound.set_volume(0.1)

    def play_bg_music(self):
        """plays video game background music"""
        self.bg_music.play(loops=-1) #play forever
        self.bg_music.set_volume(0.3)

    def stop_bg_music(self):
        """stops video game background music"""
        self.bg_music.stop()