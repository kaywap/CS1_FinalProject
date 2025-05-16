#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Heads Down! Multiplayer Poker Game
    A networked Texas Hold'em poker implementation
"""

__author__ = 'Kayla Cao'
__version__ = '1.0.0'

import os
import sys
import socket
import threading

import pygame

# Local module imports
from config import *
from deck import Deck
from hand import Hand
from player import Player
from input_handler import InputHandler
from button import Button
from hand_evaluator import HandEvaluator
from game_over_handler import GameOverHandler
from sounds import SoundManager
from network_manager import NetworkManager
from poker_network_manager import PokerNetworkManager
from card import Card


class MultiplayerPokerGame:
    def __init__(self, is_server=False, server_ip='127.0.0.1'):
        # Pygame initialization
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Heads Down! Multiplayer Poker')

        # Network configuration
        self.is_server = is_server
        self.player_id = 0  # 0 for server, 1 for client
        self.network_manager = PokerNetworkManager(
            game=self,
            is_server=is_server,
            server_ip=server_ip
        )

        # Game state initialization
        self._init_game_state()
        self._create_ui_components()

    def _init_game_state(self):
        # Players and game mechanics
        self.player1 = Player()
        self.player2 = Player()
        self.community_cards = Player()
        self.community_cards.cards_visible = True

        # Game variables
        self.pot = 0
        self.hand_evaluator = HandEvaluator()
        self.game_over_handler = GameOverHandler()
        self.sound_manager = SoundManager()

        # State tracking
        self.status_message = ''
        self.small_blind = 0
        self.big_blind = 0
        self.current_player = None
        self.game_state = STATE_PREFLOP

    def _create_ui_components(self):
        # Fonts and buttons setup
        self.font = pygame.font.SysFont(None, 36)
        self.button_font = pygame.font.SysFont(None, 24)

        # Button creation
        self.buttons = pygame.sprite.Group(
            Button(50, 550, 80, 40, 'Cards', self.button_font),
            Button(150, 550, 80, 40, 'Call', self.button_font),
            Button(250, 550, 80, 40, 'Raise', self.button_font),
            Button(350, 550, 80, 40, 'Fold', self.button_font),
            Button(450, 550, 80, 40, 'Check', self.button_font)
        )

    def handle_network_action(self, action, amount=0):
        """Process actions from network"""
        action_handlers = {
            'fold': self.handle_fold,
            'call': self.handle_call,
            'raise': lambda: self.handle_raise(amount),
            'check': self.handle_check
        }

        handler = action_handlers.get(action)
        if handler:
            handler()

    def run(self):
        """Main game loop with network support"""
        self.network_manager.start()

        clock = pygame.time.Clock()
        running = True

        while running:
            self._handle_events()
            self._update_game_state()
            self._render_game()

            pygame.display.flip()
            clock.tick(30)

        pygame.quit()
        sys.exit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            # Add more event handling logic

    def _update_game_state(self):
        # Network state synchronization
        pass

    def _render_game(self):
        # Render game UI
        pass


def main():
    """Entry point for multiplayer poker game"""
    print('Multiplayer Poker Setup')
    print('1. Host Game')
    print('2. Join Game')

    choice = input('Select mode (1/2): ')

    game = MultiplayerPokerGame(
        is_server=choice == '1',
        server_ip=input('Server IP: ') if choice == '2' else None
    )
    game.run()


if __name__ == '__main__':
    main()