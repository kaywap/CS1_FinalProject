"""player.py"""
__version__ = '05/22/2025'
__author__ = 'Kayla Cao'

import pygame
from hand import Hand
from config import *
from input_handler import InputHandler

class Player:
    def __init__(self):
        """Initialization"""
        self.hand = Hand()
        self.balance = 0
        self.password = None
        self.current_bet = 0
        self.is_folded = False
        self.cards_visible = False  # Track if cards are currently visible
        self.is_all_in = False  # Track if player is all-in

    def set_balance(self, screen, player):
        """sets the balance of the player"""
        self.balance = InputHandler.get_numeric_input(
            screen,
            "Set " + player + " balance to:",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            min_value=2
        )

    def player_bet(self, screen):
        """betting functionality"""
        # Determine maximum bet amount (can't bet more than balance + current bet)
        max_bet = self.balance + self.current_bet

        # Get bet amount from player
        current_bet = InputHandler.get_numeric_input(
            screen,
            f"Raise bet to: (Max: {max_bet})",  # Add max to the prompt for clarity
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            min_value=1,
            max_value=max_bet
        )

        # If input was cancelled (None returned), return None explicitly
        if current_bet is None:
            return None

        # Check if this is an all-in bet
        if current_bet >= max_bet:
            current_bet = max_bet
            self.is_all_in = True

        return current_bet

    def place_bet(self, amount):
        """Place a bet, deducting from balance"""
        # Validate bet amount
        if amount <= 0:
            return False

        # Handle all-in scenario
        if amount >= self.balance + self.current_bet:
            amount = self.balance + self.current_bet
            self.is_all_in = True

        # Calculate the actual amount to deduct
        amount_to_deduct = amount - self.current_bet

        # Deduct from balance and set current bet
        self.balance -= amount_to_deduct
        self.current_bet = amount
        return True

    def fold(self):
        """Player folds their hand"""
        self.is_folded = True

    def show_cards(self):
        """Make cards visible after password verification"""
        self.cards_visible = True

    def hide_cards(self):
        """Hide cards"""
        self.cards_visible = False

    def reset_for_new_hand(self):
        """Reset player state for a new hand"""
        self.hand = Hand()  # Create a new empty hand
        self.current_bet = 0
        self.is_folded = False
        self.cards_visible = False
        self.is_all_in = False
        # Note: balance is not reset between hands